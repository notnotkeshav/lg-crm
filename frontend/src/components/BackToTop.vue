<template>
  <transition name="fade">
    <button
      v-show="visible"
      @click="scrollToTop"
      class="fixed bottom-6 right-6 p-3 rounded-full bg-primary-600 text-white shadow-lg hover:bg-primary-700 focus:outline-none focus:ring-2 focus:ring-primary-500 focus:ring-offset-2 z-50 transition-all duration-300 transform hover:scale-110"
      aria-label="Back to top"
    >
      <FeatherIcon name="chevron-up" class="h-5 w-5" />
    </button>
  </transition>
</template>

<script>
import { defineComponent, ref, onMounted, onUnmounted } from 'vue'

export default defineComponent({
  name: 'BackToTop',
  props: {
    visibilityHeight: {
      type: Number,
      default: 300
    },
    scrollDuration: {
      type: Number,
      default: 500
    }
  },
  setup(props) {
    const visible = ref(false)

    const handleScroll = () => {
      visible.value = window.pageYOffset > props.visibilityHeight
    }

    const scrollToTop = () => {
      const startPosition = window.pageYOffset
      const startTime = performance.now()

      const animateScroll = (currentTime) => {
        const elapsedTime = currentTime - startTime
        const progress = Math.min(elapsedTime / props.scrollDuration, 1)
        const easeInOutCubic = progress < 0.5
          ? 4 * progress * progress * progress
          : 1 - Math.pow(-2 * progress + 2, 3) / 2

        window.scrollTo(0, startPosition * (1 - easeInOutCubic))

        if (elapsedTime < props.scrollDuration) {
          requestAnimationFrame(animateScroll)
        }
      }

      requestAnimationFrame(animateScroll)
    }

    onMounted(() => {
      window.addEventListener('scroll', handleScroll)
    })

    onUnmounted(() => {
      window.removeEventListener('scroll', handleScroll)
    })

    return {
      visible,
      scrollToTop
    }
  }
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s, transform 0.3s;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
  transform: translateY(10px);
}
</style> 