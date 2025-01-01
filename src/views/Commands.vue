<template>
  <div class="commands">
    <h1>Linguistic Tools <span class="ipa">/lɪŋˈɡwɪstɪk tuːlz/</span></h1>
    <div class="commands-grid">
      <div 
        v-for="(command, index) in commands" 
        :key="index"
        class="command-card"
      >
        <div class="card-content">
          <div class="card-icon" :class="command.icon">
            <span class="icon-emoji">{{ command.emoji }}</span>
          </div>
          <h3>{{ command.name }}</h3>
          <p>{{ command.description }}</p>
          <div class="card-footer">
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'

const commands = ref([
  {
    name: 'IPA',
    description: 'Convert text into International Phonetic Alphabet notation for precise pronunciation guidance',
    icon: 'ipa-icon',
    emoji: '🔉'
  },
  {
    name: 'Translate',
    description: 'Translate text between multiple languages with natural language processing',
    icon: 'translate-icon',
    emoji: '🌍'
  },
  {
    name: 'Syllabify',
    description: 'Break down words into syllables and analyze their phonological structure',
    icon: 'syllable-icon',
    emoji: '📝'
  },
  {
    name: 'Tree',
    description: 'Generate detailed syntax trees to visualize sentence structure',
    icon: 'tree-icon',
    emoji: '🌳'
  },
  {
    name: 'Logic',
    description: 'Convert natural language into formal logical representations',
    icon: 'logic-icon',
    emoji: '🧮'
  },
  {
    name: 'Morphology',
    description: 'Analyze word structure, identifying roots, affixes, and formation patterns',
    icon: 'morphology-icon',
    emoji: '📚'
  }
])
</script>

<style scoped>
.commands {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  min-height: 100vh;
}

h1 {
  text-align: center;
  color: #2c3e50;
  font-size: 2.8rem;
  margin-bottom: 3rem;
  text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
}

.ipa {
  display: block;
  font-family: 'Noto Sans', sans-serif;
  color: #666;
  font-size: 1rem;
  text-shadow: none;
}

.commands-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1.5rem;
  margin-top: 2rem;
}

.command-card {
  background: white;
  padding: 1.5rem;
  border-radius: 12px;
  box-shadow: 0 4px 6px rgba(0,0,0,0.1);
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
  border: 2px solid #e1e8f0;
  position: relative;
  overflow: hidden;
}

.command-card:hover {
  transform: translateY(-5px) scale(1.02);
  box-shadow: 0 12px 20px rgba(0,0,0,0.15);
  border-color: #4a90e2;
}

.command-card:hover h3 {
  color: #4a90e2;
}

.command-card:hover .icon-emoji {
  transform: scale(1.2) rotate(5deg);
}

.icon-emoji {
  font-size: 1.8rem;
  transition: transform 0.3s ease;
  display: inline-block;
}

.card-content {
  transition: transform 0.3s ease;
}

.command-card:hover .card-content {
  transform: translateY(-2px);
}

.command-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: linear-gradient(90deg, #4a90e2, #67b26f);
}

.command-card:hover::before {
  opacity: 0.8;
  background: linear-gradient(90deg, #4a90e2, #67b26f, #4a90e2);
  background-size: 200% 100%;
  animation: gradientShift 3s ease infinite;
}

@keyframes gradientShift {
  0% { background-position: 0% 50%; }
  50% { background-position: 100% 50%; }
  100% { background-position: 0% 50%; }
}

.ipa-icon { background-image: url(''); }
.translate-icon { background-image: url(''); }
.syllable-icon { background-image: url(''); }
.tree-icon { background-image: url(''); }
.logic-icon { background-image: url(''); }
.morphology-icon { background-image: url(''); }

code {
  display: block;
  background: #f8f9fa;
  padding: 0.8rem;
  border-radius: 6px;
  margin-top: 1rem;
  border: 1px dashed #ccd;
  font-family: 'Fira Code', monospace;
}
</style>
