param([string]$SourcePath, [string]$OutDir = $PSScriptRoot)
# Saved-row transfer only; no transcriptome rescan. PowerShell 7, no added packages.
$ErrorActionPreference = 'Stop'
$pin = 'dece8fd886f554641a6c32276b00731af0d05438'
$expected = 'ffec759ac33c734d8aa28aa2f71f9f2b5e8296c8ece0e21f8a744606ba1d37ec'
$sourceUrl = "https://raw.githubusercontent.com/trimcrae/Rare-cancers/$pin/research/autonomy/continuation-2026-10-02/results/aso-transcriptome.json"
if ($SourcePath) { $bytes = [IO.File]::ReadAllBytes((Resolve-Path -LiteralPath $SourcePath)) }
else {
    $client = [Net.Http.HttpClient]::new(); $client.Timeout = [TimeSpan]::FromSeconds(30)
    try { $bytes = $client.GetByteArrayAsync($sourceUrl).GetAwaiter().GetResult() } finally { $client.Dispose() }
}
$hash = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes)).ToLowerInvariant()
if ($hash -ne $expected -or $bytes.Length -ne 435970) { throw 'Frozen source hash/size mismatch' }
$source = [Text.Encoding]::UTF8.GetString($bytes) | ConvertFrom-Json
if ($source.designs.Count -ne 220 -or @($source.designs.design_id | Sort-Object -Unique).Count -ne 220) { throw 'Design identity scope' }
function Choice($rows, $gapName, $hammingName) {
    $gap = ($rows | Measure-Object -Property $gapName -Minimum).Minimum
    $primary = @($rows | Where-Object { $_.$gapName -eq $gap })
    $hamming = ($primary | Measure-Object -Property $hammingName -Maximum).Maximum
    return @{primary=@($primary.donor_bases | Sort-Object); final=@(($primary | Where-Object { $_.$hammingName -eq $hamming }).donor_bases | Sort-Object)}
}
function Same($a,$b) { return (($a -join ',') -eq ($b -join ',')) }
$table = @(); $rankingIds = @{}
foreach ($r in $source.rankings) {
    if ($rankingIds.ContainsKey($r.junction)) { throw 'Duplicate ranking junction' }; $rankingIds[$r.junction]=$true
    $ds = @($source.designs | Where-Object junction -eq $r.junction)
    if ($ds.Count -ne 5 -or !(Same @($ds.donor_bases | Sort-Object) @(6,7,8,9,10))) { throw 'Junction placements' }
    if (@($ds | Where-Object { $_.control -ne $r.control -or $_.evidence_class -ne $r.evidence_class }).Count) { throw 'Evidence/control mismatch' }
    if (@($ds | Where-Object { $null -eq $_.union_hamming -or $_.union_hamming_lower_bound -ne $_.union_hamming -or $_.union_hamming_upper_bound -ne $_.union_hamming }).Count) { throw 'Unresolved Hamming values' }
    $old = Choice $ds 'archive_gap' 'archive_hamming'; $new = Choice $ds 'union_gap' 'union_hamming'
    foreach ($k in @('primary','final')) {
        if (!(Same $old[$k] $r.('archive_'+$k)) -or !(Same $new[$k] $r.('union_'+$k))) { throw "Choice mismatch $($r.junction) $k" }
        if ((!(Same $old[$k] $new[$k])) -ne $r.($k+'_changed')) { throw 'Saved changed flag mismatch' }
    }
    foreach ($d in $ds) {
        if (($old.primary -contains $d.donor_bases) -ne $d.archive_primary -or ($old.final -contains $d.donor_bases) -ne $d.archive_final) { throw 'Archived row flags mismatch' }
    }
    $selected = @($ds | Where-Object { $new.final -contains $_.donor_bases } | Sort-Object donor_bases)
    $table += [pscustomobject][ordered]@{junction=$r.junction;evidence_class=$r.evidence_class;control=$r.control;
        archive_final_offsets=$old.final -join ',';union_final_offsets=$new.final -join ',';
        final_changed=!(Same $old.final $new.final);final_disjoint=(@($old.final | Where-Object { $new.final -contains $_ }).Count -eq 0);
        union_selected_antisense_5to3=($selected | ForEach-Object { "d$($_.donor_bases):$($_.antisense)" }) -join ';';
        union_gap_max_nt=($selected.union_gap | Sort-Object -Unique) -join ',';
        union_min_hamming=($selected.union_hamming | Sort-Object -Unique) -join ','}
}
if ($table.Count -ne 44 -or @($rankingIds.Keys).Count -ne @($source.designs.junction | Sort-Object -Unique).Count) { throw 'Ranking group scope' }
$targets=@($table | Where-Object { !$_.control }); $controls=@($table | Where-Object control)
if ($targets.Count -ne 43 -or $controls.Count -ne 1 -or @($targets | Where-Object final_changed).Count -ne 41 -or @($targets | Where-Object final_disjoint).Count -ne 23) { throw 'Target counts/changes' }
[IO.Directory]::CreateDirectory($OutDir) | Out-Null
function Write-Table($name,$title,$rows,$controlNote) {
    $rows | Export-Csv (Join-Path $OutDir ($name+'.tsv')) -Delimiter "`t" -NoTypeInformation -Encoding utf8
    $lines = @('---',"id: DOC-ASO-$($name.ToUpperInvariant())-20261002", "title: $title",'kind: generated','status: generated','level: L3',
        'generator: build-expanded-choices.ps1','purpose: Transfer every tied final choice from fixed per-design sequence descriptors into a readable resource.',
        'scope: Saved-row ranking arithmetic and source-bound choices; no activity, expression or safety inference.',
        'audience: [maintainers, external reviewers]','date: "2026-10-02"','last_verified: "2026-10-02"','---','',"# $title",'',
        $controlNote,'', 'Offsets count donor bases in the forward 16-base target. Antisense sequences run 5′–3′ and retain every final tie. Gap is maximum perfect contiguous match covering the complete six-base core (nucleotides); Hamming is minimum full-window mismatch count. Primary selection minimizes gap, then final selection maximizes Hamming among ties. These sequence choices are not validated therapeutic leads.','',
        '| Junction | Evidence class | Archived final offsets | Expanded final offsets | Changed | Disjoint | Expanded selected antisense (offset:sequence) | Gap (nt) | Hamming |',
        '| --- | --- | --- | --- | --- | --- | --- | ---: | ---: |')
    foreach ($r in $rows) { $lines += "| $($r.junction) | $($r.evidence_class) | $($r.archive_final_offsets) | $($r.union_final_offsets) | $($r.final_changed) | $($r.final_disjoint) | $($r.union_selected_antisense_5to3.Replace(';','<br>')) | $($r.union_gap_max_nt) | $($r.union_min_hamming) |" }
    $lines += @('',"Source: $sourceUrl",'',"Source SHA256: ``$hash``. All ranking sets and saved changed flags were recomputed from the fixed design rows before writing this table; archived row choice flags were also checked. No transcriptome search was rerun.")
    [IO.File]::WriteAllText((Join-Path $OutDir ($name+'.md')),($lines -join "`n")+"`n",[Text.UTF8Encoding]::new($false))
}
Write-Table 'expanded-reference-choices' 'Expanded-reference choices across 43 target junctions' $targets 'This table contains all 43 target junctions (215 design records). The annotation-error control and its five designs are excluded and reported separately.'
Write-Table 'annotation-control-choices' 'Separate annotation-error control choices' $controls 'This one historical annotation-error control junction contains five designs and is excluded from the 43 target-junction and 215 target-design summaries. It is not assigned to the USZ20 model.'
$receipt=[ordered]@{status='executed-saved-row-transfer';source_revision=$pin;source_url=$sourceUrl;source_sha256=$hash;source_bytes=$bytes.Length;
    design_rows=220;target_junctions=43;control_junctions=1;target_final_changed=41;target_final_disjoint=23;
    checks=@('All44 archive and union primary/final sets recomputed','All saved changed flags matched','All220 archived row choice flags matched','All final ties retained','Full-rank minima exact');
    outputs=@(Get-ChildItem -LiteralPath $OutDir -File | Where-Object { $_.Name -match '^(expanded-reference-choices|annotation-control-choices)\.(tsv|md)$' } | Sort-Object Name | ForEach-Object { [ordered]@{name=$_.Name;bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant()} })}
$receipt | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $OutDir 'expanded-choices-receipt.json') -Encoding utf8
$receipt | ConvertTo-Json -Depth 8
