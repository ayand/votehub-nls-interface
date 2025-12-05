interface Answer {
    choice: string
    pct: number
}

interface Poll {
    id: string
    subject: string
    poll_type: string
    pollster: string
    start_date: string
    end_date: string
    sample_size: number | null
    population: string
    answers: Answer[]
    created_at: string
    url?: string
}

interface PollsTableProps {
    polls: Poll[]
    subject: string
    pollType: string
    colorMap: Record<string, string>
}

export type { Answer, Poll, PollsTableProps }
