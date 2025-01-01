<template>
  <div class="bot-interface">
    <h1>🔤 WugBot In Action <span class="subtitle">Your Linguistics Assistant</span></h1>
    
    <div class="command-interface">
      <div class="command-selector">
        <label>Select Tool:</label>
        <select v-model="selectedCommand" class="fancy-select">
          <option value="ipa">🔉 IPA Translation</option>
          <option value="translate">🌍 Language Translation</option>
          <option value="syllabify">📝 Syllabification</option>
          <option value="tree">🌳 Syntax Tree</option>
          <option value="logic">🧮 Logic</option>
          <option value="morphology">📚 Morphology</option>
        </select>
      </div>

      <div v-if="selectedCommand === 'translate'" class="translation-inputs">
        <div class="lang-select">
          <label>From:</label>
          <select v-model="fromLang" class="fancy-select">
            <option v-for="code in languageCodes" :key="code" :value="code">
              {{ getLanguageName(code) }}
            </option>
          </select>
        </div>
        <div class="lang-select">
          <label>To:</label>
          <select v-model="toLang" class="fancy-select">
            <option v-for="code in languageCodes" :key="code" :value="code">
              {{ getLanguageName(code) }}
            </option>
          </select>
        </div>
      </div>

      <div class="input-area">
        <textarea 
          v-model="inputText" 
          :placeholder="getPlaceholder()"
          class="fancy-input"
        ></textarea>
        <button @click="processCommand" :disabled="isProcessing" class="fancy-button">
          <span class="button-content">
            {{ isProcessing ? '⚡ Processing...' : '🚀 Execute' }}
          </span>
        </button>
      </div>

      <div v-if="result" class="result-area">
        <h3>🎯 Result:</h3>
        <div class="result-content" v-html="formattedResult"></div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'

const selectedCommand = ref('ipa')
const inputText = ref('')
const result = ref('')
const isProcessing = ref(false)
const fromLang = ref('en')
const toLang = ref('es')

const languageCodes = [
  'ar', 'zh', 'en', 'fr', 'de', 'hi', 'it', 
  'ja', 'pl', 'pt', 'tr', 'ru', 'es'
]

const languageNames = {
  ar: 'Arabic',
  zh: 'Chinese',
  en: 'English',
  fr: 'French',
  de: 'German',
  hi: 'Hindi',
  it: 'Italian',
  ja: 'Japanese',
  pl: 'Polish',
  pt: 'Portuguese',
  tr: 'Turkish',
  ru: 'Russian',
  es: 'Spanish'
}

const getLanguageName = (code) => languageNames[code] || code

const getPlaceholder = () => {
  const placeholders = {
    ipa: 'Enter text for IPA translation...',
    translate: 'Enter text to translate...',
    syllabify: 'Enter word(s) to syllabify...',
    tree: 'Enter a sentence for syntax tree...',
    logic: 'Enter a sentence for logical form...',
    morphology: 'Enter word(s) for morphological analysis...'
  }
  return placeholders[selectedCommand.value]
}

const formattedResult = computed(() => {
  if (!result.value) return ''
  // Replace newlines with <br> tags and preserve spaces
  return result.value.replace(/\n/g, '<br>').replace(/ /g, '&nbsp;')
})

const processCommand = async () => {
  if (!inputText.value.trim()) return
  
  isProcessing.value = true
  result.value = ''
  
  try {
    // Update the API endpoint to use the production URL when deployed
    const apiUrl = process.env.NODE_ENV === 'production' 
      ? '/api/command'  // This will be handled by Vercel routing
      : 'http://localhost:5000/api/command'
      
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        command: selectedCommand.value,
        text: inputText.value,
        fromLang: fromLang.value,
        toLang: toLang.value
      })
    })
    
    const data = await response.json()
    if (!response.ok) {
      throw new Error(data.error || `HTTP error! status: ${response.status}`)
    }
    
    result.value = data.result || 'No result returned'
  } catch (error) {
    console.error('Error:', error)
    result.value = `Error: ${error.message || 'Failed to connect to server'}`
  } finally {
    isProcessing.value = false
  }
}
</script>

<style scoped>
.bot-interface {
  max-width: 800px;
  margin: 2rem auto;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  padding: 2rem;
  border-radius: 20px;
  box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
  font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
}

h1 {
  text-align: center;
  color: #2c3e50;
  font-size: 2.5rem;
  margin-bottom: 1.5rem;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

.subtitle {
  display: block;
  font-size: 1rem;
  color: #666;
  margin-top: 0.5rem;
}

.command-interface {
  background: linear-gradient(135deg, #ffffff 0%, #f0f4f8 100%);
  padding: 2rem;
  border-radius: 15px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.05);
}

.fancy-select {
  width: 100%;
  padding: 12px;
  border: 2px solid #e1e8ed;
  border-radius: 10px;
  background: white;
  font-size: 1rem;
  transition: all 0.3s ease;
  cursor: pointer;
  appearance: none;
  background-image: url("data:image/svg+xml,...");
  background-repeat: no-repeat;
  background-position: right 12px center;
}

.fancy-select:hover {
  border-color: #3498db;
}

.fancy-input {
  width: 100%;
  padding: 1rem;
  border: 2px solid #e1e8ed;
  border-radius: 10px;
  font-size: 1rem;
  transition: all 0.3s ease;
  resize: none;
  min-height: 120px;
  background: white;
}

.fancy-input:focus {
  border-color: #3498db;
  box-shadow: 0 0 0 3px rgba(52,152,219,0.1);
  outline: none;
}

.fancy-button {
  background: linear-gradient(135deg, #3498db 0%, #2980b9 100%);
  color: white;
  border: none;
  padding: 1rem 2rem;
  border-radius: 10px;
  font-size: 1rem;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  width: 100%;
  margin-top: 1rem;
}

.fancy-button:hover:not(:disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 8px rgba(0,0,0,0.1);
}

.fancy-button:disabled {
  background: linear-gradient(135deg, #95a5a6 0%, #7f8c8d 100%);
}

.result-area {
  margin-top: 2rem;
  padding: 1.5rem;
  background: white;
  border-radius: 10px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.05);
}

.result-content {
  font-family: 'Fira Code', monospace;
  white-space: pre-wrap;
  background: #f8f9fa;
  padding: 1.5rem;
  border-radius: 8px;
  border: 2px solid #e1e8ed;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  color: #2c3e50;
  font-weight: 600;
}

.translation-inputs {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1rem;
  margin-bottom: 1rem;
}

.lang-select {
  display: flex;
  flex-direction: column;
}

@keyframes fadeIn {
  from { opacity: 0; transform: translateY(10px); }
  to { opacity: 1; transform: translateY(0); }
}

.result-area {
  animation: fadeIn 0.3s ease-out;
}
</style>
<!-- {
  "version": 2,
  "builds": [
    {
      "src": "wugWebsite.py",
      "use": "@vercel/python",
      "config": { 
        "runtime": "python3.11",
        "maxLambdaSize": "15mb"  
      }
    }
  ],
  "routes": [
    {
      "src": "/api/(.*)",
      "dest": "wugWebsite.py"
    }
  ],
  "env": {
    "PYTHONPATH": ".",
    "NLTK_DATA": "/tmp/nltk_data"  
  }
} -->