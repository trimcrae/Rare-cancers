$ErrorActionPreference = 'Stop'
$root = $PSScriptRoot
$witnesses = @(Import-Csv (Join-Path $root 'witnesses.tsv') -Delimiter "`t")
$source = Get-Content -Raw (Join-Path $root 'target-source-slice.json') | ConvertFrom-Json
$annotations = Get-Content -Raw (Join-Path $root 'ensembl-transcripts.json') | ConvertFrom-Json -AsHashtable
$apiReceipts = Get-Content -Raw (Join-Path $root 'api-receipts.json') | ConvertFrom-Json
foreach ($r in $apiReceipts) {
    if ($r.status -ne 200 -or (Get-FileHash (Join-Path $root $r.file)).Hash.ToLowerInvariant() -ne $r.sha256) { throw 'API receipt failed' }
}
$transcripts = @($witnesses | Group-Object transcript | ForEach-Object {
    $parts=$_.Name.Split('.'); $a=$annotations[$parts[0]]
    [pscustomobject][ordered]@{frozen_transcript=$_.Name;witness_gene=($_.Group.gene | Sort-Object -Unique) -join ';';
        current_id=$a.id;current_version=$a.version;version_matches=($a.version -eq [int]$parts[1]);
        current_parent_gene=$a.Parent;current_display_name=$a.display_name;current_biotype=$a.biotype;
        assembly=$a.assembly_name;available_design_window_occurrences=$_.Count;lookup_url="https://rest.ensembl.org/lookup/id/$($parts[0])?content-type=application/json"}
})
if ($transcripts.Count -ne 60 -or @($transcripts | Where-Object { !$_.current_biotype -or !$_.version_matches }).Count) { throw 'Unresolved transcript/version: report explicitly before proceeding' }
$targets = @($source.designs | ForEach-Object {
    $d=$_; $w=@($witnesses | Where-Object design_id -eq $d.design_id)
    $n=0; $genes=@()
    foreach ($s in $d.strata.psobject.Properties.Value) { if ($s.min_hamming -eq 0) { $n += $s.nearest_occurrences; $genes += $s.nearest_genes } }
    $types=@($w | ForEach-Object { $annotations[$_.transcript.Split('.')[0]].biotype } | Group-Object | Sort-Object Name)
    [pscustomobject][ordered]@{design_id=$d.design_id;evidence_class=$d.evidence_class;target_5to3=$d.target;
        full_census_exact_occurrences=$n;available_witness_occurrences=$w.Count;unreported_occurrences=($n-$w.Count);
        witnesses_complete=($w.Count -eq $n);full_census_genes=($genes | Sort-Object -Unique) -join ';';
        saved_transcripts=($w.transcript | Sort-Object -Unique) -join ';';
        current_biotype_counts_saved_only=($types | ForEach-Object { "$($_.Name):$($_.Count)" }) -join ';'}
})
$targets | Export-Csv (Join-Path $root 'target-annotations.tsv') -Delimiter "`t" -NoTypeInformation -Encoding utf8
$transcripts | Sort-Object frozen_transcript | Export-Csv (Join-Path $root 'transcript-annotations.tsv') -Delimiter "`t" -NoTypeInformation -Encoding utf8
$n=($targets | Measure-Object full_census_exact_occurrences -Sum).Sum
$summary=[ordered]@{source_revision=$source.revision;original_result_sha256=$source.original_result_sha256;
    annotation_release=(Get-Content -Raw (Join-Path $root 'ensembl-release.json') | ConvertFrom-Json).releases;
    targets=$targets.Count;distinct_targets=@($targets.target_5to3 | Sort-Object -Unique).Count;
    distinct_frozen_witness_transcripts=$transcripts.Count;resolved_version_matching_transcripts=$transcripts.Count;
    full_census_genes=@($targets.full_census_genes | Sort-Object -Unique).Count;
    exact_design_record_window_occurrences=$n;available_witness_occurrences=$witnesses.Count;
    available_occurrence_fraction=($witnesses.Count/$n);omitted_occurrences=($n-$witnesses.Count);
    complete_target_witness_lists=@($targets | Where-Object witnesses_complete).Count;
    capped_target_witness_lists=@($targets | Where-Object { !$_.witnesses_complete }).Count;
    saved_occurrence_biotypes=@($witnesses | ForEach-Object { $annotations[$_.transcript.Split('.')[0]].biotype } | Group-Object | Sort-Object Name | ForEach-Object { [ordered]@{biotype=$_.Name;count=$_.Count} });
    unique_transcript_biotypes=@($transcripts | Group-Object current_biotype | Sort-Object Name | ForEach-Object { [ordered]@{biotype=$_.Name;count=$_.Count} });
    limits=@('Current Ensembl release116 annotations, not separately frozen GENCODE50 biotype annotations; stable transcript versions agree but do not prove immutable annotation labels.',
      'Biotype proportions concern the saved capped witness list only; six unsaved occurrences remain unclassified.',
      'Counts refer to design-record-window occurrences, not independent transcripts, patients or genes; overlapping targets and transcript aliases recur.',
      'All-gene labels come from uncapped original nearest_genes census; transcript identities and biotypes only from available first20 witnesses per design/stratum.',
      'No inference of expression, transcript abundance, cleavage, selectivity, safety or clinical risk.')}
$summary | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $root 'summary.json') -Encoding utf8
$files=Get-ChildItem -LiteralPath $root -File | Where-Object Name -ne 'receipt.json' | Sort-Object Name | ForEach-Object { [ordered]@{name=$_.Name;bytes=$_.Length;sha256=(Get-FileHash -LiteralPath $_.FullName).Hash.ToLowerInvariant()} }
[ordered]@{status='executed';method='Current Ensembl lookup/id annotation of only saved independently verified exact-match witnesses';source_revision=$source.revision;files=@($files)} | ConvertTo-Json -Depth 8 | Set-Content (Join-Path $root 'receipt.json') -Encoding utf8
$summary | ConvertTo-Json -Depth 8
