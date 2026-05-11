import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader } from "@/components/ui/card";

export default function PlannerPage() {
  return (
    <Card className="mx-auto max-w-2xl">
      <CardHeader>
        <h1 className="text-xl font-semibold">Plan a new trip</h1>
      </CardHeader>
      <CardContent>
        <form className="grid gap-4">
          <input
            className="h-10 rounded-md border border-slate-200 px-3"
            placeholder="Destination"
          />
          <div className="grid gap-4 md:grid-cols-2">
            <input
              className="h-10 rounded-md border border-slate-200 px-3"
              placeholder="Budget"
            />
            <input
              className="h-10 rounded-md border border-slate-200 px-3"
              placeholder="Travelers"
            />
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <input
              className="h-10 rounded-md border border-slate-200 px-3"
              placeholder="Start date"
              type="date"
            />
            <input
              className="h-10 rounded-md border border-slate-200 px-3"
              placeholder="End date"
              type="date"
            />
          </div>
          <input
            className="h-10 rounded-md border border-slate-200 px-3"
            placeholder="Interests (hiking, food, culture)"
          />
          <Button type="submit">Generate itinerary</Button>
        </form>
      </CardContent>
    </Card>
  );
}
