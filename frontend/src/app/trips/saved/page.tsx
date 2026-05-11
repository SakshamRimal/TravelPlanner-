import { Card, CardContent, CardHeader } from "@/components/ui/card";

const savedTrips = [
  { id: "save-1", title: "Lisbon Food Tour" },
  { id: "save-2", title: "Reykjavik Northern Lights" },
];

export default function SavedTripsPage() {
  return (
    <section className="grid gap-4">
      <h1 className="text-2xl font-semibold">Saved trips</h1>
      <div className="grid gap-4 md:grid-cols-2">
        {savedTrips.map((trip) => (
          <Card key={trip.id}>
            <CardHeader>
              <h3 className="text-lg font-semibold">{trip.title}</h3>
            </CardHeader>
            <CardContent>
              <p className="text-sm text-slate-600">
                Ready to finalize? Open the planner to continue.
              </p>
            </CardContent>
          </Card>
        ))}
      </div>
    </section>
  );
}
