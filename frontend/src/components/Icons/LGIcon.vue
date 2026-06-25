<template>
  <svg
    xmlns="http://www.w3.org/2000/svg"
    viewBox="0 0 200 100"
    role="img"
    aria-label="LG Logo"
    class="lg-logo"
  >
    <!-- Outer circle -->
    <circle cx="50" cy="50" r="45" fill="#a50034" />
    
    <!-- Inner 'L' -->
    <rect x="35" y="20" width="10" height="40" fill="#fff" />
    <rect x="35" y="50" width="20" height="10" fill="#fff" />
    
    <!-- Inner 'G' -->
    <path
      d="M70 40c0-5.5-4.5-10-10-10s-10 4.5-10 10 4.5 10 10 10c2.8 0 5.4-1.2 7.2-3l-4-3h7v10h-10l3-4.8C65.4 48.2 63.8 50 60 50c-5.5 0-10-4.5-10-10s4.5-10 10-10 10 4.5 10 10z"
      fill="#fff"
    />
    
    <!-- LG Text -->
    <text
      x="120"
      y="60"
      font-family="Arial, sans-serif"
      font-size="40"
      fill="#555"
    >
      LG
    </text>
  </svg>
</template>

<script>
export default {
  name: "LgLogo",
};
</script>

<style scoped>
.lg-logo {
  width: 200px;
  height: auto;
}
</style>