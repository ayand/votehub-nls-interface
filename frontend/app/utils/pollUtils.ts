import { Poll, Answer } from '../models'

export interface ChoiceData {
  displayName: string
  average: number
  color: string
}

// Normalize choice names by removing periods, commas, and extra whitespace
export const normalizeChoice = (choice: string): string => {
  return choice
    .replace(/\./g, '') // Remove periods
    .replace(/,/g, '') // Remove commas
    .replace(/\s+/g, ' ') // Normalize whitespace
    .trim()
}

// Calculate normalized choices with colors from polls data
export const calculateChoicesWithColors = (
  polls: Poll[],
  colorMap: Record<string, string>
): ChoiceData[] => {
  // Calculate unique choices for this group of polls with normalization
  const choiceStats = new Map<string, { total: number; count: number; displayName: string; originalNames: string[] }>()

  polls.forEach((poll: Poll) => {
    poll.answers?.forEach((answer: Answer) => {
      const normalized = normalizeChoice(answer.choice)
      const stats = choiceStats.get(normalized) || { total: 0, count: 0, displayName: normalized, originalNames: [] }
      stats.total += answer.pct
      stats.count += 1
      stats.originalNames.push(answer.choice)
      // Use the shortest version as display name (usually the one without periods)
      if (answer.choice.length < stats.displayName.length) {
        stats.displayName = answer.choice
      }
      choiceStats.set(normalized, stats)
    })
  })

  // Sort choices by average percentage in descending order
  const uniqueChoices = Array.from(choiceStats.entries())
    .map(([normalized, stats]) => ({
      normalized,
      displayName: stats.displayName,
      average: stats.total / stats.count
    }))
    .sort((a, b) => b.average - a.average)

  // Return top 10 choices with colors
  return uniqueChoices
    .slice(0, 10)
    .map(item => ({
      displayName: item.displayName,
      average: item.average,
      color: colorMap[item.displayName] || '#7f7f7f'
    }))
}
