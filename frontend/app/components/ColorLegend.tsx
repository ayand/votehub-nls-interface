import React from 'react'

interface LegendItem {
  displayName: string
  color: string
}

interface ColorLegendProps {
  items: LegendItem[]
}

export default function ColorLegend({ items }: ColorLegendProps) {
  if (items.length === 0) {
    return null
  }

  return (
    <div style={{
      marginBottom: '1.5rem',
      backgroundColor: '#ffffff',
      border: '1px solid #e5e7eb',
      borderRadius: '8px',
      boxShadow: '0 1px 3px rgba(0, 0, 0, 0.1)',
      overflow: 'hidden'
    }}>
      <h3 style={{
        fontSize: '1rem',
        fontWeight: '600',
        color: '#1e40af',
        padding: '0.75rem 1rem',
        margin: 0,
        borderBottom: '1px solid #e5e7eb',
        backgroundColor: '#f9fafb'
      }}>
        Color Legend
      </h3>

      <div style={{
        overflowX: 'auto',
        overflowY: 'hidden',
        padding: '1rem'
      }}>
        <div style={{
          display: 'flex',
          flexDirection: 'row',
          gap: '1rem',
          minWidth: 'min-content'
        }}>
          {items.map((item) => (
            <div
              key={item.displayName}
              style={{
                display: 'flex',
                flexDirection: 'row',
                alignItems: 'center',
                gap: '0.5rem',
                minWidth: 'fit-content',
                flexShrink: 0,
                padding: '0.5rem 0.75rem',
                backgroundColor: '#f9fafb',
                borderRadius: '6px',
                border: '1px solid #e5e7eb'
              }}
            >
              <div
                style={{
                  width: '20px',
                  height: '20px',
                  backgroundColor: item.color,
                  borderRadius: '4px',
                  border: '1px solid #d1d5db',
                  flexShrink: 0
                }}
              />

              <div style={{
                fontSize: '0.9rem',
                fontWeight: '500',
                color: '#374151',
                fontFamily: 'system-ui, -apple-system, sans-serif',
                whiteSpace: 'nowrap'
              }}>
                {item.displayName}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  )
}
