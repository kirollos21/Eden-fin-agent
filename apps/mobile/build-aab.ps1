# Build Android App Bundle (.aab) Script
# This script helps build the .aab file for the Eden mobile app

Write-Host "Building Android App Bundle (.aab) for Eden Mobile App" -ForegroundColor Green
Write-Host "==================================================" -ForegroundColor Green

# Check if we're in the correct directory
if (-not (Test-Path "android")) {
    Write-Host "Error: android directory not found. Please run this script from the mobile app directory." -ForegroundColor Red
    exit 1
}

# Check Java version
Write-Host "Checking Java version..." -ForegroundColor Yellow
try {
    $javaVersion = java -version 2>&1 | Select-String "version"
    Write-Host "Java version: $javaVersion" -ForegroundColor Cyan
    
    # Check if Java version is compatible (should be Java 17 or 21 for Gradle 8.5)
    if ($javaVersion -match "version \"24") {
        Write-Host "Warning: Java 24 detected. This may cause compatibility issues with Gradle." -ForegroundColor Yellow
        Write-Host "Recommended: Use Java 17 or Java 21 for better compatibility." -ForegroundColor Yellow
        Write-Host "You can download Java 17 from: https://adoptium.net/temurin/releases/?version=17" -ForegroundColor Cyan
    }
} catch {
    Write-Host "Error: Java not found or not accessible." -ForegroundColor Red
    Write-Host "Please install Java 17 or 21 and ensure it's in your PATH." -ForegroundColor Yellow
    exit 1
}

# Navigate to android directory
Write-Host "Navigating to android directory..." -ForegroundColor Yellow
Set-Location android

# Clean previous builds
Write-Host "Cleaning previous builds..." -ForegroundColor Yellow
try {
    .\gradlew.bat clean
    Write-Host "Clean completed successfully." -ForegroundColor Green
} catch {
    Write-Host "Warning: Clean failed, continuing anyway..." -ForegroundColor Yellow
}

# Build the AAB file
Write-Host "Building Android App Bundle (.aab)..." -ForegroundColor Yellow
Write-Host "This may take several minutes..." -ForegroundColor Cyan

try {
    .\gradlew.bat bundleRelease
    Write-Host "Build completed successfully!" -ForegroundColor Green
    
    # Check if the AAB file was created
    $aabPath = "app\build\outputs\bundle\release\app-release.aab"
    if (Test-Path $aabPath) {
        $fileSize = (Get-Item $aabPath).Length / 1MB
        Write-Host "AAB file created successfully!" -ForegroundColor Green
        Write-Host "Location: $((Get-Location).Path)\$aabPath" -ForegroundColor Cyan
        Write-Host "Size: $([math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
    } else {
        Write-Host "Warning: AAB file not found at expected location." -ForegroundColor Yellow
        Write-Host "Please check the build output for any errors." -ForegroundColor Yellow
    }
} catch {
    Write-Host "Build failed!" -ForegroundColor Red
    Write-Host "Error details:" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    
    Write-Host "`nTroubleshooting tips:" -ForegroundColor Yellow
    Write-Host "1. Ensure you have Java 17 or 21 installed" -ForegroundColor Cyan
    Write-Host "2. Check that ANDROID_HOME environment variable is set" -ForegroundColor Cyan
    Write-Host "3. Ensure Android SDK Build Tools are installed" -ForegroundColor Cyan
    Write-Host "4. Try running: .\gradlew.bat --stacktrace bundleRelease" -ForegroundColor Cyan
}

# Return to original directory
Set-Location ..

Write-Host "`nBuild process completed." -ForegroundColor Green
