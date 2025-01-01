<template>
  <div class="dashboard">
    <div class="status-card">
      <h2>Wug Bot Status</h2>
      <div class="status-indicator" :class="{ online: botStatus === 'online' }">
        {{ botStatus }}
      </div>
      <button @click="toggleBot">{{ botStatus === 'online' ? 'Stop Bot' : 'Start Bot' }}</button>
    </div>
    
    <div class="stats-grid">
      <div class="stat-card">
        <h3>Servers</h3>
        <p>{{ serverCount }}</p>
      </div>
      <div class="stat-card">
        <h3>Active Users</h3>
        <p>{{ userCount }}</p>
      </div>
      <div class="stat-card">
        <h3>Commands Today</h3>
        <p>{{ commandCount }}</p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'

const botStatus = ref('offline')
const serverCount = ref(0)
const userCount = ref(0)
const commandCount = ref(0)

const toggleBot = () => {
  botStatus.value = botStatus.value === 'online' ? 'offline' : 'online'
  // Add actual bot control logic here
}
</script>

<style scoped>
.dashboard {
  max-width: 1200px;
  margin: 0 auto;
}

.status-card {
  background: white;
  padding: 2rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  margin-bottom: 2rem;
}

.status-indicator {
  display: inline-block;
  padding: 0.5rem 1rem;
  border-radius: 20px;
  background: #ff4757;
  color: white;
  margin: 1rem 0;
}

.status-indicator.online {
  background: #2ed573;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
  gap: 1rem;
}

.stat-card {
  background: white;
  padding: 1.5rem;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0,0,0,0.1);
  text-align: center;
}

.stat-card h3 {
  color: #2c3e50;
  margin-bottom: 0.5rem;
}

.stat-card p {
  font-size: 2rem;
  font-weight: bold;
  color: #2c3e50;
  margin: 0;
}
</style>
