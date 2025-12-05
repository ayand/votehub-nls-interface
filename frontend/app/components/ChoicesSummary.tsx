import React from 'react'

interface ChoiceData {
  displayName: string
  average: number
  color: string
}

interface ChoicesSummaryProps {
  choices: ChoiceData[]
  pollAmount: number
}

export default function ChoicesSummary({ choices, pollAmount }: ChoicesSummaryProps) {
  if (choices.length === 0) {
    return null
  }

  return (
    <div style={{
      marginBottom: '2rem',
      backgroundColor: '#ffffff',
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
      overflow: 'hidden'
    }}>
      <h3 style={{
        fontSize: '1.25rem',
        fontWeight: '600',
        color: '#1e40af',
        padding: '1rem 1.5rem',
        margin: 0,
        textAlign: 'center',
        borderBottom: '1px solid #e5e7eb'
      }}>
        Average Across {pollAmount} Polls
      </h3>

      <div style={{
        overflowX: 'auto',
        overflowY: 'hidden',
        padding: '1.5rem'
      }}>
        <div style={{
          display: 'flex',
          flexDirection: 'row',
          gap: '1.5rem',
          minWidth: 'min-content'
        }}>
          {choices.map((choice) => (
            <div
              key={choice.displayName}
              style={{
                display: 'grid',
                gridTemplateColumns: 'auto 1fr auto',
                alignItems: 'center',
                gap: '0.75rem',
                minWidth: 'fit-content',
                flexShrink: 0,
                padding: '0.5rem 1rem',
                backgroundColor: '#f9fafb',
                borderRadius: '6px',
                border: '1px solid #e5e7eb'
              }}
            >
              <div
                style={{
                  width: '24px',
                  height: '24px',
                  backgroundColor: choice.color,
                  borderRadius: '4px',
                  border: '1px solid #d1d5db',
                  flexShrink: 0
                }}
              />

              <div style={{
                fontSize: '1.1rem',
                fontWeight: '700',
                color: '#000000',
                fontFamily: 'system-ui, -apple-system, sans-serif',
                whiteSpace: 'nowrap'
              }}>
                {choice.displayName}
              </div>

              <div style={{
                fontSize: '0.95rem',
                fontWeight: '600',
                color: '#6b7280',
                fontFamily: 'system-ui, -apple-system, sans-serif',
                whiteSpace: 'nowrap'
              }}>
                {choice.average.toFixed(1)}%
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
