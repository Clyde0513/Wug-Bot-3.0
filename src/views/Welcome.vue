<template>
  <div class="welcome">
    <header class="welcome-header">
      <h1>Welcome to WugBot!</h1>
      <div class="wug-mascot">
        <img :src="wugLogo" alt="Wug Mascot" class="bounce-animation">
        <div class="subtitle">Website version of the UCLA Linguistic Server Wug Bot 3.0</div>
      </div>
    </header>

    <div class="content-sections">
      <section class="info-card">
        <h2>What is Linguistics?</h2>
        <p>Linguistics is the scientific study of language - how it works, how it's structured, and how humans use it. 
        It explores everything from sounds (phonology) to sentence structure (syntax) and meaning (semantics).</p>
      </section>

      <section class="info-card">
        <h2>Meet WugBot!</h2>
        <p>WugBot is named after the famous "wug test" - a groundbreaking experiment in linguistics that showed how 
        children understand a   nd apply language rules. Just like how children can naturally form "wugs" from "wug," 
        our bot helps you explore and understand language patterns!</p>
      </section>
      <div class="content-sections1">
      <section class="info-card fun-fact">
        <h2>🎓 Fun Linguistic Fact</h2>
        <p>Did you know? The word "goodbye" originally comes from the phrase "God be with ye"! Over time, it contracted 
        to "godbwye" and eventually became the "goodbye" we use today. This process of words changing over time is called 
        semantic change!</p>
      </section>
    </div>
    </div>
  </div>
</template>

<script>
import wugLogo from '/wugBot3.0/Wug-Bot-3.0/assets/this-is-a-wug-removebg-preview (1).png'

export default {
  name: 'Welcome',
  data() {
    return {
      wugLogo
    }
  }
}
</script>

<style scoped>
.welcome {
  max-width: 1200px;
  margin: 0 auto;
  padding: 2rem;
}

.welcome-header {
  text-align: center;
  margin-bottom: 3rem;
}

.welcome-header h1 {
  color: #2c3e50;
  font-size: 2.5rem;
  margin-bottom: 1rem;
}

.wug-mascot {
  width: 120px;
  margin: 0 auto;
}

.wug-mascot img {
  width: 100%;
}

.bounce-animation {
  animation: bounce 2s infinite;
}

.content-sections {
        grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.content-sections1{
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
}

.info-card {
  background: white;
  padding: 1.5rem;
  border-radius: 10px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transition: transform 0.3s ease;
}

.info-card:hover {
  transform: translateY(-20px);
}

.info-card h2 {
  color: #4077d7;
  margin-bottom: 1rem;
  font-size: 1.5rem;
}

.info-card p {
  color: #546e7a;
  line-height: 1.6;
}

.fun-fact {
  background: linear-gradient(135deg, #4077d7 0%, #283593 100%);
}

.fun-fact h2, .fun-fact p {
  color: white;
}

.subtitle {
  color: #666;
  font-size: 0.9rem;
  margin-top: 0.5rem;
  font-style: italic;
}

@keyframes bounce {
  0%, 100% { transform: translateY(0); }
  50% { transform: translateY(-10px); }
}
</style>
