import { Card, CardContent, CardHeader } from "@/components/ui/card";

export default function TripDetailsPage() {
  return (
    <section className="grid gap-4">
      <h1 className="text-2xl font-semibold">Trip details</h1>
      <Card>
        <CardHeader>
          <h3 className="text-lg font-semibold">Day-wise itinerary</h3>
        </CardHeader>
        <CardContent>
          <ul className="list-disc pl-4 text-sm text-slate-600">
            <li>Day 1: Arrive, local market walk, sunset view.</li>
            <li>Day 2: Hike and cultural tour.</li>
            <li>Day 3: Lake activities and cafe crawl.</li>
          </ul>
        </CardContent>
      </Card>
    </section>
  );
}
