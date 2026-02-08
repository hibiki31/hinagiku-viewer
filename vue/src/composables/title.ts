import { watch, type Ref } from 'vue'

/**
 * ページタイトルを設定するcomposable
 * @param title タイトル文字列または Ref<string>
 * @param options オプション（prefix, suffix, separator）
 */
export function useTitle(
  title: string | Ref<string>,
  options: {
    prefix?: string
    suffix?: string
    separator?: string
  } = {}
) {
  const {
    prefix = 'HinaV',
    suffix = '',
    separator = ' | '
  } = options

  const setTitle = (newTitle: string) => {
    const parts = [prefix]
    if (newTitle) {
      parts.push(newTitle)
    }
    if (suffix) {
      parts.push(suffix)
    }
    document.title = parts.join(separator)
  }

  // titleがRefの場合はwatchで追跡
  if (typeof title === 'object' && 'value' in title) {
    watch(
      title,
      (newValue) => {
        setTitle(newValue)
      },
      { immediate: true }
    )
  } else {
    // 文字列の場合は即座に設定
    setTitle(title)
  }

  return {
    setTitle
  }
}
