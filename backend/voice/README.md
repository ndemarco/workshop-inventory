# Voice Interface (Phase 6)

Natural language voice control for hands-free inventory management.

## Status: 🚧 Planned

## Planned Features

### Wake Word Activation
```
"Hey Inventory" → System activates and listens
```

### Voice Commands

#### Adding Items
```
"Add a new screw: pan head phillips, 3/4 inch long, number 8, mild steel. 
 I'm putting it in Muse, level 4, A3."

Response: "Found similar item in Zeus level 2 B4. Do you want to check that first?"
or
Response: "Added pan head phillips screw to Muse level 4 A3. Location A3 now occupied."
```

#### Searching
```
"Find me a long metric bolt, M6 diameter"

Response: "Found 3 matches:
1. M6 hex bolt, 50mm long in Zeus level 1 A5
2. M6 socket cap screw, 60mm in Muse level 2 C2  
3. M6 carriage bolt, 75mm in Zeus level 3 B1"
```

#### Moving Items
```
"Move the Arduino from Zeus A5 to Muse B2"

Response: "Moving Arduino Uno from Zeus level 1 A5 to Muse level 2 B2. 
         Location B2 is now occupied."
```

#### Querying
```
"Where are my M6 bolts?"
"What's in Muse level 4 A3?"
"How many resistors do I have?"
```

## Technical Architecture

### Components

1. **Wake Word Detection**
   - Porcupine or Snowboy
   - Low-power always-listening
   - Runs on edge device (Jetson Nano, RPi)

2. **Speech-to-Text**
   - Vosk (offline, fast)
   - Whisper (higher accuracy)
   - Supports technical vocabulary

3. **Natural Language Understanding**
   - spaCy for entity extraction
   - Custom patterns for inventory commands
   - Intent classification

4. **Command Processing**
   - Parse location addresses (Module:Level:Position)
   - Extract item specifications
   - Validate commands before execution

5. **Text-to-Speech Feedback**
   - pyttsx3 (offline)
   - Google TTS (online, better quality)
   - Confirmation and error messages

### Hardware Requirements

#### Minimum (Raspberry Pi 4)
- 4GB RAM
- USB microphone
- Audio output

#### Recommended (Jetson Nano)
- 4GB RAM
- GPU acceleration for Whisper
- Better real-time performance

### System Flow

```
┌─────────────────┐
│  Wake Word      │
│  (Always On)    │
└────────┬────────┘
         │ "Hey Inventory"
         ▼
┌─────────────────┐
│  Listen         │
│  (Record Audio) │
└────────┬────────┘
         │ Audio Data
         ▼
┌─────────────────┐
│  Speech-to-Text │
│  (Vosk/Whisper) │
└────────┬────────┘
         │ "Add bolts to Zeus A3"
         ▼
┌─────────────────┐
│  NLU Parser     │
│  (Intent+Slots) │
└────────┬────────┘
         │ {action: 'add', item: 'bolts', location: 'Zeus:1:A3'}
         ▼
┌─────────────────┐
│  Command API    │
│  (Flask)        │
└────────┬────────┘
         │ Success/Error
         ▼
┌─────────────────┐
│  Text-to-Speech │
│  (Feedback)     │
└─────────────────┘
```

## Implementation Plan

### Phase 6a: Basic Voice Commands
- Wake word detection
- Simple command parsing
- Add/search/query operations
- Text-to-speech feedback

### Phase 6b: Advanced NLU
- Complex multi-step commands
- Context awareness
- Clarification dialogues
- Error recovery

### Phase 6c: Continuous Conversation
- Multi-turn dialogues
- "What about that location?" (anaphora)
- Batch operations via conversation

## Configuration

```yaml
# voice_config.yml
wake_word:
  engine: porcupine
  keyword: "hey inventory"
  sensitivity: 0.5

speech_to_text:
  engine: vosk
  model: vosk-model-small-en-us-0.15
  sample_rate: 16000

text_to_speech:
  engine: pyttsx3
  rate: 150
  voice: default

processing:
  timeout: 5  # seconds
  confidence_threshold: 0.7
```

## Development

### Local Testing
```bash
python voice/test_stt.py "Add bolts to Zeus A3"
python voice/test_wakeword.py
```

### Integration
```bash
python voice/main.py --config voice_config.yml
```

## Dependencies

```python
# Voice-specific requirements
vosk==0.3.45
pyaudio==0.2.14
pyttsx3==2.90
pvporcupine==2.2.0  # Wake word
webrtcvad==2.0.10   # Voice activity detection
```

## Privacy & Security

- **All processing local**: No cloud services by default
- **Wake word only**: Microphone data discarded unless activated
- **No recording**: Audio processed in memory only
- **Optional cloud**: Can enable cloud STT for better accuracy

---

*This feature is planned for Phase 6 development.*
