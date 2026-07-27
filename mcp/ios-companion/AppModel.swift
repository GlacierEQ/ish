import Foundation
import SwiftUI

@MainActor
final class AppModel: ObservableObject {
    enum Domain: String, CaseIterable, Codable { case photos, documents, contacts, calendar, health, imports }
    struct AuditEntry: Identifiable, Codable { let id = UUID(); let date = Date(); let domain: Domain; let action: String; let count: Int }
    @Published private(set) var auditEntries: [AuditEntry] = []
    @Published var lastError: String?

    // Persist a user’s actual consent choices in protected storage, not just UI state.
    private let defaults = UserDefaults.standard
    func isEnabled(_ domain: Domain) -> Bool { defaults.bool(forKey: "consent." + domain.rawValue) }
    func setEnabled(_ value: Bool, for domain: Domain) { defaults.set(value, forKey: "consent." + domain.rawValue) }
    func record(_ domain: Domain, action: String, count: Int) { auditEntries.insert(.init(domain: domain, action: action, count: count), at: 0) }
    func fail(_ error: Error) { lastError = error.localizedDescription }
}

struct ExportEnvelope<Payload: Codable>: Codable {
    let id: String
    let exportedAt: Date
    let source: String
    let payload: Payload
    let consentPurpose: String
}
