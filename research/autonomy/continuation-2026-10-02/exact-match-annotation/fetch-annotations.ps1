$ErrorActionPreference = 'Stop'
$annotationRoot = $PSScriptRoot
$client = [System.Net.Http.HttpClient]::new()
$client.Timeout = [TimeSpan]::FromSeconds(45)
$receipts = [System.Collections.Generic.List[object]]::new()
function Read-Annotation($name, $url, $payload) {
    $request = [System.Net.Http.HttpRequestMessage]::new()
    $request.RequestUri = $url
    $request.Method = if ($null -eq $payload) { [System.Net.Http.HttpMethod]::Get } else { [System.Net.Http.HttpMethod]::Post }
    $request.Headers.Accept.ParseAdd('application/json')
    if ($null -ne $payload) { $request.Content = [System.Net.Http.StringContent]::new($payload, [Text.Encoding]::UTF8, 'application/json') }
    $received = [DateTime]::UtcNow.ToString('o')
    try {
        $response = $client.SendAsync($request).GetAwaiter().GetResult()
        $bytes = $response.Content.ReadAsByteArrayAsync().GetAwaiter().GetResult()
        if ($bytes.Length -gt 250000) { throw 'Response exceeds bounded annotation cap' }
        [IO.File]::WriteAllBytes((Join-Path $annotationRoot $name), $bytes)
        $sha = [Convert]::ToHexString([Security.Cryptography.SHA256]::HashData($bytes)).ToLowerInvariant()
        $receipts.Add([ordered]@{file=$name;url=$url;method=$request.Method.Method;request_payload=$payload;status=[int]$response.StatusCode;bytes=$bytes.Length;sha256=$sha;retrieved_utc=$received})
    } catch { $receipts.Add([ordered]@{file=$name;url=$url;method=$request.Method.Method;request_payload=$payload;retrieved_utc=$received;error=$_.Exception.Message}) }
    finally { $request.Dispose() }
}
$ids = @(Import-Csv (Join-Path $annotationRoot 'witnesses.tsv') -Delimiter "`t" | ForEach-Object { $_.transcript.Split('.')[0] } | Sort-Object -Unique)
Read-Annotation 'ensembl-release.json' 'https://rest.ensembl.org/info/data?content-type=application/json' $null
Read-Annotation 'ensembl-transcripts.json' 'https://rest.ensembl.org/lookup/id' (@{ids=$ids} | ConvertTo-Json -Compress)
$receipts | ConvertTo-Json -Depth 8 | Set-Content -LiteralPath (Join-Path $annotationRoot 'api-receipts.json') -Encoding utf8
$client.Dispose()
$receipts | Select-Object file,status,bytes,error | ConvertTo-Json -Compress
