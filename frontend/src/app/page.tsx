import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

const highlights = [
  "Autonomous trip planning",
  "Day-wise itineraries",
  "Budget estimates",
  "AI travel assistant",
];

export default function HomePage() {
  return (
    <section className="grid gap-6">
      <div className="grid gap-4">
        <p className="text-sm font-semibold text-brand-700">Plan smarter</p>
        <h1 className="text-3xl font-semibold">
          Your AI travel co-pilot for effortless trips
        </h1>
        <p className="text-slate-600">
          Search destinations, get flights and hotel suggestions, and generate
          complete itineraries tailored to your budget and interests.
        </p>
        <div className="flex flex-wrap gap-3">
          <Button asChild>
            <Link href="/planner">Start planning</Link>
          </Button>
          <Button asChild variant="outline">
            <Link href="/chat">Ask the AI assistant</Link>
          </Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2">
        {highlights.map((item) => (
          <Card key={item}>
            <CardHeader>
              <h3 className="text-lg font-semibold">{item}</h3>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-600">
                Built for modern travelers with smart recommendations and
                optimized schedules.
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
