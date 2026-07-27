import Contacts

struct ContactPayload: Codable { let givenName: String; let familyName: String; let organization: String; let phoneNumbers: [String]; let emails: [String] }
final class ContactsImporter {
    private let store = CNContactStore()
    func exportApprovedContacts() throws -> [ExportEnvelope<ContactPayload>] {
        // Add only fields the user-facing consent screen explicitly offers.
        let keys: [CNKeyDescriptor] = [CNContactGivenNameKey as CNKeyDescriptor, CNContactFamilyNameKey as CNKeyDescriptor, CNContactOrganizationNameKey as CNKeyDescriptor, CNContactPhoneNumbersKey as CNKeyDescriptor, CNContactEmailAddressesKey as CNKeyDescriptor]
        let request = CNContactFetchRequest(keysToFetch: keys)
        var result: [ExportEnvelope<ContactPayload>] = []
        try store.enumerateContacts(with: request) { c, _ in
            let payload = ContactPayload(givenName: c.givenName, familyName: c.familyName, organization: c.organizationName, phoneNumbers: c.phoneNumbers.map { $0.value.stringValue }, emails: c.emailAddresses.map { $0.value as String })
            result.append(.init(id: c.identifier, exportedAt: .now, source: "contacts", payload: payload, consentPurpose: "contacts fields approved by user"))
        }
        return result
    }
}
