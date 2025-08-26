# Building Android App Bundle (.aab) for Eden Mobile App

This guide will help you generate the Android App Bundle (.aab) file for the Eden mobile app.

## Prerequisites

### 1. Java Development Kit (JDK)
- **Required**: Java 17 or Java 21
- **Current Issue**: You have Java 24 installed, which is not compatible with Gradle 8.5
- **Solution**: Install Java 17 or 21 from [Eclipse Temurin](https://adoptium.net/temurin/releases/)

### 2. Android SDK
- Android SDK Platform Tools
- Android SDK Build Tools (version 34.0.0 or higher)
- Android SDK Platform (API level 34 or higher)

### 3. Environment Variables
Set the following environment variables:
```powershell
ANDROID_HOME=C:\Users\[YourUsername]\AppData\Local\Android\Sdk
JAVA_HOME=C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot
```

## Build Methods

### Method 1: Using EAS Build (Recommended - Cloud Build)
```bash
# Login to EAS
eas login

# Build for Android
eas build --platform android --profile production
```

**Note**: This requires access to the EAS project. If you don't have access, contact the project owner.

### Method 2: Local Build (Alternative)
```bash
# Navigate to mobile directory
cd apps/mobile

# Run the build script
.\build-aab.ps1
```

### Method 3: Manual Gradle Build
```bash
# Navigate to android directory
cd apps/mobile/android

# Clean previous builds
.\gradlew.bat clean

# Build the AAB
.\gradlew.bat bundleRelease
```

## Troubleshooting

### Java Version Issues
If you encounter "Unsupported class file major version 68" error:

1. **Install Java 17 or 21**:
   - Download from [Eclipse Temurin](https://adoptium.net/temurin/releases/)
   - Install and set as default Java version

2. **Update JAVA_HOME**:
   ```powershell
   setx JAVA_HOME "C:\Program Files\Eclipse Adoptium\jdk-17.0.x-hotspot"
   ```

3. **Verify Java version**:
   ```bash
   java -version
   ```

### EAS Build Permission Issues
If you get permission errors with EAS:

1. **Check current user**:
   ```bash
   eas whoami
   ```

2. **Request access** from the project owner (the-commit-company)

3. **Alternative**: Create a new EAS project under your account

### Android SDK Issues
If Android SDK is not found:

1. **Install Android Studio** and Android SDK
2. **Set ANDROID_HOME** environment variable
3. **Install required SDK components**:
   - Android SDK Platform 34
   - Android SDK Build Tools 34.0.0
   - Android SDK Platform Tools

## Expected Output

After successful build, you should find the .aab file at:
```
apps/mobile/android/app/build/outputs/bundle/release/app-release.aab
```

## File Information
- **Package Name**: `ai.eden.app`
- **Version**: 1.1.3
- **Target SDK**: 34
- **Minimum SDK**: 21

## Next Steps

1. **Test the AAB**: Upload to Google Play Console for testing
2. **Sign the AAB**: Ensure it's signed with the correct keystore
3. **Upload to Play Store**: Use the AAB for production release

## Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify all prerequisites are met
3. Contact the development team for assistance
