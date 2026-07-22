from ..models import Contact
from ..repositories.contact_repository import ContactRepository

class ContactService:
    @staticmethod
    def import_contacts_from_csv(client, file_obj, stage):
        import csv
        import io
        
        decoded_file = file_obj.read().decode('utf-8-sig')
        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)
        
        imported_count = 0
        errors = []
        
        for index, row in enumerate(reader, start=2):
            name = row.get('name', '').strip()
            phone = row.get('phone_number', '').strip()
            email = row.get('email', '').strip()
            
            if not name or not phone:
                errors.append(f"Row {index}: Missing name or phone_number.")
                continue
                
            # Basic deduplication by phone
            if ContactRepository.filter_contacts(client=client, phone_number=phone).exists():
                errors.append(f"Row {index}: Contact with phone {phone} already exists.")
                continue
                
            ContactRepository.create_contact(
                client=client,
                name=name,
                phone_number=phone,
                email=email,
                stage=stage
            )
            imported_count += 1
            
        return {
            "message": f"Successfully imported {imported_count} contacts.",
            "errors": errors
        }

    @staticmethod
    def export_contacts_to_csv(client):
        from django.http import HttpResponse
        import csv
        
        contacts = ContactRepository.filter_contacts(client=client)
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="contacts.csv"'
        
        writer = csv.writer(response)
        writer.writerow(['PlatformID', 'Name', 'Phone', 'Email', 'Stage', 'Tags', 'Notes', 'Created At'])
        
        for contact in contacts:
            writer.writerow([
                contact.platform_id,
                contact.name or '',
                contact.phone_number or '',
                contact.email or '',
                contact.stage,
                ','.join(contact.tags),
                contact.notes or '',
                contact.created_at.strftime("%Y-%m-%d %H:%M:%S")
            ])
            
        return response
