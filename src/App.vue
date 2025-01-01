<template>
  <div class="app">
    <nav class="sidebar">
      <div class="logo">
        <img :src="wugLogo" alt="WugBot Logo">
        <h1>WugBot</h1>
        <div class="subtitle">Here to serve you!</div>
      </div>
      <ul class="nav-links">
        <li><router-link to="/welcome">Home</router-link></li>
        <li><router-link to="/">Linguistic Tools</router-link></li>
        <li><router-link to="/interact">Interact with Wug Bot!</router-link></li>
      </ul>
    </nav>
    <main class="content">
      <router-view></router-view>
    </main>
  </div>
</template>

<script>
import wugLogo from '../assets/this-is-a-wug-removebg-preview (1).png'

export default {
  name: 'App',
  data() {
    return {
      wugLogo
    }
  }
}
</script>

<style scoped>
.app {
  display: flex;
  min-height: 100vh;
}

.sidebar {
  width: 280px;
  background: linear-gradient(180deg, #4077d7 0%, #283593 100%);
  color: white;
  padding: 1.5rem;
  box-shadow: 2px 0 5px rgba(0, 0, 0, 0.1);
}

.logo {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 2.5rem;
  padding-bottom: 1.5rem;
  border-bottom: 1px solid rgba(255, 255, 255, 0.1);
}

.logo img {
  width: 60px;
  height: 60px;
  filter: drop-shadow(0 2px 4px rgba(0, 0, 0, 0.2));
}

.logo h1 {
  font-size: 1.8rem;
  font-weight: 600;
  margin: 0;
}

.subtitle {
  font-size: 0.9rem;
  color: rgba(255, 255, 255, 0.8);
  font-style: italic;
}

.nav-links {
  list-style: none;
  padding: 0;
  margin: 0;
}

.nav-links li a {
  display: block;
  padding: 1rem 1.2rem;
  color: rgba(255, 255, 255, 0.9);
  text-decoration: none;
  border-radius: 6px;
  margin-bottom: 0.5rem;
  font-weight: 500;
  transition: all 0.3s ease;
}

.nav-links li a:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateX(5px);
}

.nav-links li a.router-link-active {
  background: rgba(255, 255, 255, 0.2);
  color: white;
}

.content {
  flex: 1;
  padding: 2rem;
  background: #f5f6fa;
}
</style>
