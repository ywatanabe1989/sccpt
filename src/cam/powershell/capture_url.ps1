# Capture URL screenshot using headless Edge WebView2
# Works with Windows host URLs from WSL without opening visible browser

param(
    [Parameter(Mandatory=$true)]
    [string]$Url,

    [Parameter(Mandatory=$false)]
    [int]$Width = 1920,

    [Parameter(Mandatory=$false)]
    [int]$Height = 1080,

    [Parameter(Mandatory=$false)]
    [string]$OutputFormat = "base64"
)

Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Windows.Forms

try {
    # Use WebBrowser control (headless, no visible window)
    $webBrowser = New-Object System.Windows.Forms.WebBrowser
    $webBrowser.ScriptErrorsSuppressed = $true
    $webBrowser.Size = New-Object System.Drawing.Size($Width, $Height)
    $webBrowser.ScrollBarsEnabled = $false

    # Navigate to URL
    $webBrowser.Navigate($Url)

    # Wait for page to load
    while ($webBrowser.ReadyState -ne 4) {
        Start-Sleep -Milliseconds 100
        [System.Windows.Forms.Application]::DoEvents()
    }

    # Give extra time for rendering
    Start-Sleep -Seconds 2

    # Capture the WebBrowser control
    $bitmap = New-Object System.Drawing.Bitmap($webBrowser.Width, $webBrowser.Height)
    $webBrowser.DrawToBitmap($bitmap, $webBrowser.ClientRectangle)

    # Convert to base64
    $stream = New-Object System.IO.MemoryStream
    $bitmap.Save($stream, [System.Drawing.Imaging.ImageFormat]::Png)
    $bytes = $stream.ToArray()
    $base64 = [Convert]::ToBase64String($bytes)

    $result = @{
        Success = $true
        Url = $Url
        Width = $bitmap.Width
        Height = $bitmap.Height
        Base64Data = $base64
        Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    }

    $result | ConvertTo-Json -Depth 2 -Compress

    # Cleanup
    $webBrowser.Dispose()
    $bitmap.Dispose()
    $stream.Dispose()

} catch {
    $errorResult = @{
        Success = $false
        Url = $Url
        Error = $_.Exception.Message
        Timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    }

    $errorResult | ConvertTo-Json -Depth 2 -Compress
    exit 1
}

