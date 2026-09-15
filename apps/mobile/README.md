# TruthLens Mobile (Flutter Client)

Production-grade cross-platform mobile client for **TruthLens** built with Flutter & Dart, implementing Material 3 research-grade UI patterns, sound null safety, and responsive navigation.

## Architecture

- **Clean Architecture Layers**:
  - `lib/models/`: Strongly typed Dart data models with sound null-safety and defensive JSON decoders.
  - `lib/services/`: Platform-aware HTTP network client with automatic IP mapping (`10.0.2.2` for Android Emulator, `127.0.0.1` for iOS Simulator / Web) and JWT authorization token persistence.
  - `lib/widgets/`: Modular UI widgets including `CredibilityGauge` with calibrated color thresholds.
  - `lib/screens/`: 
    - `HomeScreen`: Interactive workspace for Full Article, Headline, and SSRF-safe URL analysis with quick benchmark loaders.
    - `ResultScreen`: Probabilistic consensus breakdown, constituent model probabilities, extracted claims table, and attributed evidence cards.
    - `HistoryScreen`: Historical verification log with pull-to-refresh and item deletion.
    - `ModelsScreen`: Live model registry and holdout test set evaluation benchmarks.

## Getting Started

### Prerequisites
- Flutter SDK `>=3.10.0`
- TruthLens backend running on `http://127.0.0.1:8000`

### Running the App

1. Navigate to the mobile directory:
   ```bash
   cd apps/mobile
   ```

2. Fetch Flutter dependencies:
   ```bash
   flutter pub get
   ```

3. Launch on your target device:
   - **Android Emulator**:
     ```bash
     flutter run -d android
     ```
     *(The app automatically connects to `http://10.0.2.2:8000/api/v1`)*
   - **iOS Simulator**:
     ```bash
     flutter run -d ios
     ```
     *(Connects to `http://127.0.0.1:8000/api/v1`)*
   - **Flutter Web**:
     ```bash
     flutter run -d chrome
     ```
