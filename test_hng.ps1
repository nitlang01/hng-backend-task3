# test_hng.ps1
# Local API test script for HNG backend task
# Run your FastAPI app first with: uvicorn main:app --reload

Write-Host "=== Starting Local API Tests ===" -ForegroundColor Cyan
$baseUrl = "http://127.0.0.1:8000"

function Invoke-Test {
    param(
        [string]$Method,
        [string]$Url,
        [string]$Desc,
        [hashtable]$Body = @{}
    )

    Write-Host "`n--- Testing: $Desc ($Method $Url)" -ForegroundColor Yellow
    try {
        if ($Method -eq "GET") {
            if ($Url -match "image") {
                $output = "summary_test.png"
                Invoke-RestMethod -Uri $Url -Method GET -OutFile $output -ErrorAction Stop
                Write-Host "[PASS] $Desc - Image received ($output)" -ForegroundColor Green
            }
            else {
                $response = Invoke-RestMethod -Uri $Url -Method GET -ErrorAction Stop
                Write-Host "[PASS] $Desc - JSON OK" -ForegroundColor Green
                $response | ConvertTo-Json -Depth 4 | Write-Host
            }
        }
        elseif ($Method -eq "POST") {
            $response = Invoke-RestMethod -Uri $Url -Method POST -Body ($Body | ConvertTo-Json) -ContentType "application/json" -ErrorAction Stop
            Write-Host "[PASS] $Desc - POST OK" -ForegroundColor Green
            $response | ConvertTo-Json -Depth 4 | Write-Host
        }
        elseif ($Method -eq "DELETE") {
            $response = Invoke-RestMethod -Uri $Url -Method DELETE -ErrorAction Stop
            Write-Host "[PASS] $Desc - DELETE OK" -ForegroundColor Green
            $response | ConvertTo-Json -Depth 4 | Write-Host
        }
        else {
            Write-Host "[WARN] Unsupported method: $Method" -ForegroundColor Yellow
        }
    }
    catch {
        Write-Host "[FAIL] $Desc - FAILED" -ForegroundColor Red
        Write-Host $_.Exception.Message -ForegroundColor DarkRed
    }
}

# Run endpoint tests
Invoke-Test -Method "POST" -Url "$baseUrl/countries/refresh" -Desc 'POST Refresh Endpoint'
Invoke-Test -Method "GET" -Url "$baseUrl/countries" -Desc 'Get All Countries (Basic)'
Invoke-Test -Method "GET" -Url "$baseUrl/countries/Nigeria" -Desc 'Get Single Country (Nigeria)'
Invoke-Test -Method "DELETE" -Url "$baseUrl/countries/Nigeria" -Desc 'Delete Country (Nigeria)'
Invoke-Test -Method "GET" -Url "$baseUrl/status" -Desc 'Status Endpoint'
Invoke-Test -Method "GET" -Url "$baseUrl/countries/image" -Desc 'Image Endpoint'

Write-Host "`n=== All tests completed ===" -ForegroundColor Cyan
Write-Host "If most of the lines above are green, your API is working correctly!"
