import json
import requests
from datetime_helper import DatetimeHelper
from authorization.access_token_handler import AccessTokenHandler

class ActivityFetcher():

    def __init__(self):
        self.token_handler = AccessTokenHandler()
        self.token_handler.acquire_permissions()
        self.access_token = self.token_handler.get_existing_access_token()
        self.dt = DatetimeHelper()

    def _get_page(self, page_number):
        query = 'https://www.strava.com/api/v3/activities'
        response = requests.get(
            query,
            headers={
                'Content-Type': 'application/json',
                'Authorization': 'Bearer {}'.format(self.access_token)
            },
            params={
                'page': page_number
            }
        )

        if response.status_code != 200:
            self.token_handler.refresh_existing_access_token()
            raise Exception('Access token error - refreshing access token, message={}'.format(response.json()))

        return response.json()

    def get_activities_since_date(self, date):
        page_number = 1
        matching_activites = []
        search_complete = False

        while not search_complete:
            activities = self._get_page(page_number)
            if not activities:
                break

            for item in activities:
                item_date = self.dt.string_to_datetime(item['start_date'])
                
                if (item_date > date):
                    matching_activites.append(item)
                else:
                    search_complete = True
            
            page_number += 1
        
        return matching_activites



# if __name__ == '__main__':
#     activity_fetcher = ActivityFetcher()
#     activity_fetcher.get_activities_since_date(datetime.strptime("2023-03-15T14:00:36Z", '%Y-%m-%dT%H:%M:%SZ'))

