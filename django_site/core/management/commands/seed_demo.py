from datetime import date

from django.core.management.base import BaseCommand

from core.models import Project, Service, Testimonial


class Command(BaseCommand):
    help = "Load polished demo services, projects, and testimonials. Safe to run again."

    def handle(self, *args, **options):
        services = [
            {
                "title": "Design & Build",
                "slug": "design-build",
                "short_description": "One accountable team from first sketch to final handover.",
                "description": "We combine architectural planning, engineering coordination, permitting support, procurement, and construction under one practical delivery plan. You get clearer costs, faster decisions, and fewer handoff delays.",
                "icon": "01",
                "image_url": "https://images.unsplash.com/photo-1503387762-592deb58ef4e?auto=format&fit=crop&w=1200&q=85",
                "featured": True,
                "display_order": 1,
            },
            {
                "title": "Residential Construction",
                "slug": "residential-construction",
                "short_description": "Thoughtful homes engineered for daily life and tropical conditions.",
                "description": "From compact family homes to premium residences, we manage structural works, architectural finishes, MEP coordination, quality checks, and turnover documentation with careful attention to the approved plan.",
                "icon": "02",
                "image_url": "https://images.unsplash.com/photo-1600585154340-be6161a56a0c?auto=format&fit=crop&w=1200&q=85",
                "featured": True,
                "display_order": 2,
            },
            {
                "title": "Commercial Construction",
                "slug": "commercial-construction",
                "short_description": "Functional spaces that support customers, teams, and growth.",
                "description": "We deliver offices, retail spaces, restaurants, clinics, and mixed-use properties with disciplined scheduling, site coordination, and finish standards aligned with your operations and brand.",
                "icon": "03",
                "image_url": "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?auto=format&fit=crop&w=1200&q=85",
                "featured": True,
                "display_order": 3,
            },
            {
                "title": "Renovation & Fit-out",
                "slug": "renovation-fit-out",
                "short_description": "Transform existing spaces with minimal operational disruption.",
                "description": "Our renovation team handles demolition planning, structural assessment, space reconfiguration, fit-out, finishes, and MEP upgrades while protecting active areas and controlling dust, noise, and downtime.",
                "icon": "04",
                "image_url": "https://images.unsplash.com/photo-1581578731548-c64695cc6952?auto=format&fit=crop&w=1200&q=85",
                "featured": True,
                "display_order": 4,
            },
            {
                "title": "Project Management",
                "slug": "project-management",
                "short_description": "Reliable control over scope, schedule, cost, safety, and quality.",
                "description": "We represent the owner's interests through planning, bidding support, contractor coordination, progress measurement, documentation, quality inspections, change control, and closeout management.",
                "icon": "05",
                "image_url": "https://images.unsplash.com/photo-1531834685032-c34bf0d84c77?auto=format&fit=crop&w=1200&q=85",
                "featured": True,
                "display_order": 5,
            },
            {
                "title": "Repairs & Maintenance",
                "slug": "repairs-maintenance",
                "short_description": "Practical corrective work that protects your property investment.",
                "description": "We assess and repair waterproofing failures, concrete defects, roof issues, worn finishes, and small MEP concerns, with clear findings and sensible recommendations before work begins.",
                "icon": "06",
                "image_url": "https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?auto=format&fit=crop&w=1200&q=85",
                "featured": True,
                "display_order": 6,
            },
        ]
        for data in services:
            Service.objects.update_or_create(slug=data["slug"], defaults=data)

        projects = [
            {
                "title": "Solana Family Residence",
                "slug": "solana-family-residence",
                "category": Project.Category.RESIDENTIAL,
                "location": "Nuvali, Laguna",
                "summary": "A warm, climate-responsive two-storey home built around light, airflow, and family connection.",
                "description": "BuildCore delivered the complete structural and architectural package for this modern tropical residence. Deep roof lines, shaded glazing, cross ventilation, and durable low-maintenance finishes help the home stay comfortable year-round. Weekly progress reports and finish mockups kept owner decisions timely and documented.",
                "client_name": "Private homeowner",
                "completion_date": date(2026, 5, 18),
                "duration_months": 11,
                "area_sqm": 286,
                "image_url": "https://images.unsplash.com/photo-1600566753190-17f0baa2a6c3?auto=format&fit=crop&w=1600&q=88",
                "featured": True,
                "published": True,
            },
            {
                "title": "Meridian Corporate Hub",
                "slug": "meridian-corporate-hub",
                "category": Project.Category.COMMERCIAL,
                "location": "Makati City",
                "summary": "A high-performance office fit-out designed for focus, collaboration, and flexible team growth.",
                "description": "The project involved phased fit-out works across an occupied building, including modular meeting areas, acoustic treatments, lighting upgrades, custom joinery, and coordinated data and power distribution. Careful sequencing allowed the client to continue operations throughout construction.",
                "client_name": "Meridian Business Group",
                "completion_date": date(2026, 2, 27),
                "duration_months": 5,
                "area_sqm": 1140,
                "image_url": "https://images.unsplash.com/photo-1497366811353-6870744d04b2?auto=format&fit=crop&w=1600&q=88",
                "featured": True,
                "published": True,
            },
            {
                "title": "Southline Logistics Center",
                "slug": "southline-logistics-center",
                "category": Project.Category.INDUSTRIAL,
                "location": "Cabuyao, Laguna",
                "summary": "A durable warehouse and dispatch facility planned for safer, faster daily movement.",
                "description": "BuildCore coordinated civil, structural, warehouse-floor, drainage, loading-bay, and administrative-office packages. The team's method statements and hold-point inspections focused on slab flatness, drainage performance, traffic flow, and safe equipment access.",
                "client_name": "Southline Distribution Inc.",
                "completion_date": date(2025, 11, 8),
                "duration_months": 9,
                "area_sqm": 4800,
                "image_url": "https://images.unsplash.com/photo-1586528116311-ad8dd3c8310d?auto=format&fit=crop&w=1600&q=88",
                "featured": True,
                "published": True,
            },
            {
                "title": "Calamba Heritage Renovation",
                "slug": "calamba-heritage-renovation",
                "category": Project.Category.RENOVATION,
                "location": "Calamba City, Laguna",
                "summary": "A careful restoration that preserved character while improving safety and comfort.",
                "description": "The team retained significant architectural details while strengthening selected structural members, replacing failed waterproofing, upgrading electrical and plumbing lines, and adapting the interior for modern family life.",
                "client_name": "Private homeowner",
                "completion_date": date(2025, 8, 15),
                "duration_months": 7,
                "area_sqm": 215,
                "image_url": "https://images.unsplash.com/photo-1600607687920-4e2a09cf159d?auto=format&fit=crop&w=1600&q=88",
                "featured": False,
                "published": True,
            },
            {
                "title": "Arc & Bean Café",
                "slug": "arc-and-bean-cafe",
                "category": Project.Category.COMMERCIAL,
                "location": "Tagaytay City",
                "summary": "A compact café fit-out with durable finishes and a memorable customer flow.",
                "description": "Work included space planning, service-counter fabrication, kitchen coordination, lighting, ventilation, wall finishes, and outdoor seating improvements. Material selections balanced visual warmth with easy maintenance.",
                "client_name": "Arc & Bean Foods",
                "completion_date": date(2025, 4, 21),
                "duration_months": 3,
                "area_sqm": 168,
                "image_url": "https://images.unsplash.com/photo-1554118811-1e0d58224f24?auto=format&fit=crop&w=1600&q=88",
                "featured": False,
                "published": True,
            },
            {
                "title": "Verde Courtyard Homes",
                "slug": "verde-courtyard-homes",
                "category": Project.Category.RESIDENTIAL,
                "location": "Santa Rosa, Laguna",
                "summary": "A small residential development organized around shade, greenery, and walkable shared spaces.",
                "description": "BuildCore delivered four coordinated units with standardized structural details, shared procurement, individual quality records, and staggered handovers. Courtyard landscaping and shaded passages create a calmer community environment.",
                "client_name": "Verde Living Corp.",
                "completion_date": date(2024, 12, 10),
                "duration_months": 14,
                "area_sqm": 920,
                "image_url": "https://images.unsplash.com/photo-1600047509807-ba8f99d2cdde?auto=format&fit=crop&w=1600&q=88",
                "featured": False,
                "published": True,
            },
        ]
        for data in projects:
            Project.objects.update_or_create(slug=data["slug"], defaults=data)

        testimonials = [
            {
                "client_name": "Andrea M.",
                "client_role": "Homeowner, Laguna",
                "quote": "The weekly updates were clear, every variation was explained before work continued, and the finished home feels even better than the drawings.",
                "rating": 5,
                "featured": True,
            },
            {
                "client_name": "Paolo Reyes",
                "client_role": "Operations Director, Meridian Business Group",
                "quote": "BuildCore worked around our operating hours and delivered the office in phases. Their documentation and site coordination made a difficult fit-out manageable.",
                "rating": 5,
                "featured": True,
            },
            {
                "client_name": "Carla Santos",
                "client_role": "Property Manager, Calamba",
                "quote": "They did not just cover the visible damage. They found the source of the leak, documented it properly, and gave us a repair plan we could understand.",
                "rating": 5,
                "featured": True,
            },
        ]
        for data in testimonials:
            Testimonial.objects.update_or_create(
                client_name=data["client_name"], defaults=data
            )

        self.stdout.write(
            self.style.SUCCESS(
                f"Demo content ready: {len(services)} services, "
                f"{len(projects)} projects, {len(testimonials)} testimonials."
            )
        )
