name: Build Flet APK
on: [push, workflow_dispatch]

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install Flet and Dependencies
        run: |
          pip install flet pypdf

      - name: Setup Java JDK
        uses: actions/setup-java@v4
        with:
          distribution: 'temurin'
          java-version: '17'

      - name: Install Ninja Build
        run: sudo apt-get install -y ninja-build

      - name: Build APK
        run: flet build apk

      - name: Upload APK Artifact
        uses: actions/upload-artifact@v4
        with:
          name: audiobook-app
          path: build/apk/*.apk
