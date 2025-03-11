import requests
import time
from django.core.management.base import BaseCommand
from yourapp.models import FPLTeam

FPL_OVERALL_LEAGUE_ID = 314
FPL_API_URL = f"https://fantasy.premierleague.com/api/leagues-classic/{FPL_LEAGUE_ID}/standings/"
RATE_LIMIT_SECONDS = 2  # Delay between API requests to prevent hitting limits

class Command(BaseCommand):
    help = "Scrape FPL Classic League Standings and store in the database with pagination support"

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting FPL data scraping...")

        # Find the last processed rank to pick up from where it left off
        last_processed_rank = FPLTeam.objects.order_by("-rank").values_list("rank", flat=True).first() or 0
        self.stdout.write(f"Resuming from rank: {last_processed_rank}")

        current_page = 1
        has_next = True

        while has_next:
            # Request data from the API with pagination
            response = requests.get(FPL_API_URL, params={"page": current_page})
            if response.status_code != 200:
                self.stderr.write(f"Error fetching page {current_page}: {response.status_code}")
                break

            data = response.json()
            teams_data = data.get("standings", {}).get("results", [])
            has_next = data.get("standings", {}).get("has_next", False)

            if not teams_data:
                self.stdout.write("No more teams found. Stopping...")
                break

            for team in teams_data:
                fpl_id = team.get("id")
                player_name = team.get("player_name")
                entry_name = team.get("entry_name")
                total_points = team.get("total")
                rank = team.get("rank")
                last_rank = team.get("last_rank")

                # Skip teams that have already been processed
                if rank <= last_processed_rank:
                    continue

                if not all([fpl_id, player_name, entry_name, total_points is not None, rank, last_rank]):
                    self.stderr.write(f"Skipping incomplete data for {player_name}")
                    continue

                # Update or create the team entry in the database
                team_obj, created = FPLTeam.objects.update_or_create(
                    fpl_id=fpl_id,
                    defaults={
                        "player_name": player_name,
                        "entry_name": entry_name,
                        "total_points": total_points,
                        "rank": rank,
                        "last_rank": last_rank,
                    },
                )

                action = "Created" if created else "Updated"
                self.stdout.write(f"{action} team: {entry_name} ({player_name}) - Rank: {rank}")

            # Progress to the next page
            current_page += 1

            # Rate limiting to prevent API overload
            self.stdout.write(f"Waiting {RATE_LIMIT_SECONDS} seconds before next request...")
            time.sleep(RATE_LIMIT_SECONDS)

        self.stdout.write(self.style.SUCCESS("FPL data scraping completed successfully!"))
