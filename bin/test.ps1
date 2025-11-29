# PowerShell version of bin/test.sh (no wait loop)
# Run with: powershell -ExecutionPolicy Bypass -File bin/test.ps1

$BASE_URL = "http://127.0.0.1:8080"

function PostJson($Url, $Object) {
    $json = $Object | ConvertTo-Json -Depth 5
    $response = Invoke-WebRequest `
        -Uri $Url `
        -Method POST `
        -Body $json `
        -ContentType "application/json" `
        -UseBasicParsing
    return $response.Content
}

function GetJson($Url) {
    $response = Invoke-WebRequest `
        -Uri $Url `
        -Method GET `
        -UseBasicParsing
    return $response.Content
}

Write-Host "=== Starting messaging-service tests (PowerShell) ==="

Write-Host "`n>>> Health check"
Invoke-WebRequest -Uri "$BASE_URL/healthz" -UseBasicParsing | Select-Object StatusCode, Content | Format-List

Write-Host "`n>>> Test 1: Outbound SMS"
$smsOutbound = @{
    from      = "+15551234567"
    to        = "+15557654321"
    type      = "sms"
    body      = "Hello from PS test"
    timestamp = "2025-11-28T00:00:00Z"
}
PostJson "$BASE_URL/api/messages/sms" $smsOutbound | Write-Host

Write-Host "`n>>> Test 2: Outbound MMS"
$outboundMms = @{
    from      = "+12016661234"
    to        = "+18045551234"
    type      = "mms"
    body      = "Hello! This is a test MMS message with attachment."
    attachments = @("https://example.com/image.jpg")
    timestamp = "2024-11-01T14:00:00Z"
}
PostJson "$BASE_URL/api/messages/sms" $outboundMms | Write-Host


Write-Host "`n>>> Test 3: Outbound Email"
$emailOutbound = @{
    from        = "user@example.com"
    to          = "friend@example.com"
    body        = "Hello from email test"
    attachments = @("https://example.com/file1.txt")
    timestamp   = "2025-11-28T00:30:00Z"
}
PostJson "$BASE_URL/api/messages/email" $emailOutbound | Write-Host

Write-Host "`n>>> Test 4: Inbound SMS Webhook"
$smsWebhook = @{
    from                  = "+15557654321"
    to                    = "+15551234567"
    type                  = "sms"
    messaging_provider_id = "provider-12345"
    body                  = "Inbound reply"
    timestamp             = "2025-11-28T01:00:00Z"
}
PostJson "$BASE_URL/api/webhooks/sms" $smsWebhook | Write-Host

Write-Host "`n>>> Test 5: Incoming MMS Webhook"
$inboundMms = @{
    from                  = "+18045551234"
    to                    = "+12016661234"
    type                  = "mms"
    messaging_provider_id = "message-2"
    body                  = "This is an incoming MMS message"
    attachments           = @("https://example.com/received-image.jpg")
    timestamp             = "2024-11-01T14:00:00Z"
}
PostJson "$BASE_URL/api/webhooks/sms" $inboundMms | Write-Host


Write-Host "`n>>> Test 6: Inbound Email Webhook"
$emailWebhook = @{
    from        = "friend@example.com"
    to          = "user@example.com"
    xillio_id   = "xillio-999"
    body        = "Inbound email reply"
    attachments = @("https://example.com/attachment.png")
    timestamp   = "2025-11-28T01:30:00Z"
}
PostJson "$BASE_URL/api/webhooks/email" $emailWebhook | Write-Host

Write-Host "`n>>> Test 7: List Conversations"
GetJson "$BASE_URL/api/conversations" | Write-Host

Write-Host "`n>>> Test 8: List Messages for Conversation 1"
GetJson "$BASE_URL/api/conversations/1/messages" | Write-Host

Write-Host "`n=== Completed all tests ==="
