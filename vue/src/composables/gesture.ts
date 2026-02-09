/**
 * マウス・タッチジェスチャー認識 composable
 */
import { ref, watchEffect, onBeforeUnmount, type Ref } from 'vue'

export interface GestureHandlers {
  onSwipeLeft?: () => void
  onSwipeRight?: () => void
  onSwipeUp?: () => void
  onSwipeDown?: () => void
  onPress?: () => void
  onTap?: () => void
}

export function useGesture(
  elementRef: Ref<HTMLElement | null>,
  handlers: GestureHandlers
) {
  const startX = ref(0)
  const startY = ref(0)
  const startTime = ref(0)
  const isPressing = ref(false)
  const pressTimer = ref<number | null>(null)
  const hasMoved = ref(false)

  const SWIPE_THRESHOLD = 50 // スワイプと判定する最小距離（ピクセル）
  const PRESS_DURATION = 500 // 長押しと判定する時間（ミリ秒）
  const TAP_MAX_DURATION = 300 // タップと判定する最大時間（ミリ秒）
  const TAP_MAX_DISTANCE = 10 // タップと判定する最大移動距離（ピクセル）

  const handlePointerDown = (e: PointerEvent) => {
    // 右クリック（コンテキストメニュー）は無視
    if (e.button === 2) {
      return
    }

    startX.value = e.clientX
    startY.value = e.clientY
    startTime.value = Date.now()
    hasMoved.value = false
    isPressing.value = true

    // 長押し検出タイマー
    if (handlers.onPress) {
      pressTimer.value = window.setTimeout(() => {
        if (isPressing.value && !hasMoved.value) {
          handlers.onPress?.()
          isPressing.value = false // 長押し発火後は無効化
        }
      }, PRESS_DURATION)
    }
  }

  const handlePointerMove = (e: PointerEvent) => {
    if (!isPressing.value) return

    const deltaX = Math.abs(e.clientX - startX.value)
    const deltaY = Math.abs(e.clientY - startY.value)

    // 移動があったらタップ・長押しではない
    if (deltaX > TAP_MAX_DISTANCE || deltaY > TAP_MAX_DISTANCE) {
      hasMoved.value = true
      if (pressTimer.value !== null) {
        clearTimeout(pressTimer.value)
        pressTimer.value = null
      }
    }
  }

  const handlePointerUp = (e: PointerEvent) => {
    if (!isPressing.value) return

    const deltaX = e.clientX - startX.value
    const deltaY = e.clientY - startY.value
    const duration = Date.now() - startTime.value
    const absX = Math.abs(deltaX)
    const absY = Math.abs(deltaY)

    // 長押しタイマーをクリア
    if (pressTimer.value !== null) {
      clearTimeout(pressTimer.value)
      pressTimer.value = null
    }

    isPressing.value = false

    // スワイプ判定
    if (absX > SWIPE_THRESHOLD || absY > SWIPE_THRESHOLD) {
      // 横スワイプが優先（横の移動量が縦より大きい）
      if (absX > absY) {
        if (deltaX > 0) {
          handlers.onSwipeRight?.()
        } else {
          handlers.onSwipeLeft?.()
        }
      } else {
        // 縦スワイプ
        if (deltaY > 0) {
          handlers.onSwipeDown?.()
        } else {
          handlers.onSwipeUp?.()
        }
      }
      return
    }

    // タップ判定
    if (
      !hasMoved.value &&
      duration < TAP_MAX_DURATION &&
      absX < TAP_MAX_DISTANCE &&
      absY < TAP_MAX_DISTANCE
    ) {
      handlers.onTap?.()
    }
  }

  const handlePointerCancel = () => {
    isPressing.value = false
    if (pressTimer.value !== null) {
      clearTimeout(pressTimer.value)
      pressTimer.value = null
    }
  }

  // 要素がマウントされたらイベントリスナーを追加
  watchEffect((onCleanup) => {
    const element = elementRef.value
    if (!element) return

    element.addEventListener('pointerdown', handlePointerDown)
    element.addEventListener('pointermove', handlePointerMove)
    element.addEventListener('pointerup', handlePointerUp)
    element.addEventListener('pointercancel', handlePointerCancel)

    onCleanup(() => {
      element.removeEventListener('pointerdown', handlePointerDown)
      element.removeEventListener('pointermove', handlePointerMove)
      element.removeEventListener('pointerup', handlePointerUp)
      element.removeEventListener('pointercancel', handlePointerCancel)
    })
  })

  onBeforeUnmount(() => {
    if (pressTimer.value !== null) {
      clearTimeout(pressTimer.value)
    }
  })

  return {
    isPressing
  }
}
