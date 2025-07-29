import { Metadata } from 'next'
import PricingSection from '@/components/PricingSection'

export const metadata: Metadata = {
    title: '定价方案 - Video2Doc',
    description: '选择适合你的Video2Doc套餐，从基础版到专业版，灵活定价满足不同需求',
}

export default function PricingPage() {
    return (
        <main className="min-h-screen">
            <PricingSection />
        </main>
    )
} 