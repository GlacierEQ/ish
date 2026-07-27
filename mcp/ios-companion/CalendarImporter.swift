import EventKit

struct CalendarPayload: Codable { let title: String; let start: Date; let end: Date; let calendarTitle: String }
final class CalendarImporter {
    private let store = EKEventStore()
    func exportEvents(from start: Date, through end: Date) -> [ExportEnvelope<CalendarPayload>] {
        precondition(end > start && end.timeIntervalSince(start) <= 366 * 86_400, "Use a bounded calendar window")
        let predicate = store.predicateForEvents(withStart: start, end: end, calendars: nil)
        return store.events(matching: predicate).map { event in
            .init(id: event.eventIdentifier ?? UUID().uuidString, exportedAt: .now, source: "calendar", payload: .init(title: event.title ?? "", start: event.startDate, end: event.endDate, calendarTitle: event.calendar.title), consentPurpose: "user-approved date window")
        }
    }
}
