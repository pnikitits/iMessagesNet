import objc
from Contacts import CNContactStore, CNContactFetchRequest, CNContactFormatter, CNContactPhoneNumbersKey, CNContactFormatterStyleFullName
from Foundation import NSAutoreleasePool
import json



def fetch_contacts(verbose=False) -> dict:
    data = {}
    error = objc.nil

    contact_store = CNContactStore.alloc().init()
    keys_to_fetch = [CNContactFormatter.descriptorForRequiredKeysForStyle_(CNContactFormatterStyleFullName), CNContactPhoneNumbersKey]
    fetch_request = CNContactFetchRequest.alloc().initWithKeysToFetch_(keys_to_fetch)

    def handler(contact, stop):
        full_name = CNContactFormatter.stringFromContact_style_(contact, CNContactFormatterStyleFullName)
        phone_numbers = [phone.value().stringValue() for phone in contact.phoneNumbers()]

        # remove spaces from phone numbers
        phone_numbers = [phone.replace(" ", "") for phone in phone_numbers]

        data[full_name] = phone_numbers

    success = contact_store.enumerateContactsWithFetchRequest_error_usingBlock_(fetch_request, error, handler)

    if not success:
        print(f"Error fetching contacts: {error}")
        return {}

    print(json.dumps(data, indent=4)) if verbose else None
    return data
    


if __name__ == '__main__':
    print(json.dumps(fetch_contacts(verbose=True), indent=4))