import { Card, CardContent, CardHeader } from "@/components/ui/card";

const trips = [
  { id: "trip-1", title: "Pokhara Adventure", dates: "May 12 - May 16" },
  { id: "trip-2", title: "Kyoto Temples", dates: "Jun 3 - Jun 6" },
];

export default function DashboardPage() {
  return (
    <section className="grid gap-4">
      <h1 className="text-2xl font-semibold">Your trips</h1>
      <div className="grid gap-4 md:grid-cols-2">
        {trips.map((trip) => (
          <Card key={trip.id}>
            <CardHeader>
              <h3 className="text-lg font-semibold">{trip.title}</h3>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-600">{trip.dates}</p>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
