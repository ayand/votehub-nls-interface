'use client'

import React from 'react'

interface AttributionProps {
    centered?: boolean
}

export default function Attribution({ centered = false }: AttributionProps) {
    return (
        <div style={{
            fontSize: '0.85rem',
            color: '#6b7280',
            marginTop: '2rem',
            padding: '1rem 1.5rem',
            backgroundColor: '#f9fafb',
            borderTop: '1px solid #e5e7eb',
            fontFamily: 'system-ui, -apple-system, sans-serif',
            textAlign: centered ? 'center' : 'left',
            lineHeight: 1.6,
        }}>
            Polling data ©{" "}
            <a
                href="https://votehub.com/polls/api/"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                    color: '#3b82f6',
                    textDecoration: 'none',
                    fontWeight: 500,
                }}
            >
                VoteHub
            </a>
            , licensed under{" "}
            <a
                href="https://creativecommons.org/licenses/by/4.0/"
                target="_blank"
                rel="noopener noreferrer"
                style={{
                    color: '#3b82f6',
                    textDecoration: 'none',
                    fontWeight: 500,
                }}
            >
                CC BY 4.0
            </a>
            . Data may be transformed or visualized by this site and does not imply
            endorsement by VoteHub.
        </div>
    )
}
