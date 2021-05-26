from exceptions.ProfileResponseError import ProfileResponseError
from exceptions.AuthenticationError import AuthenticationError
from .settings import BetSettings
from time import sleep
from requests import Response
from requests import post, get

class Core:
    settings: BetSettings

    balance: float = -1

    def __init__(self, settings: BetSettings):
        self.settings = settings

    def get_user_balance(self) -> float:
        ''' Returns user pittersons balance '''
        if self.balance == -1:
            # Get balance from website
            api_url = f'https://api.johnpittertv.com/user/{self.settings.APP_TWITCH_NICKNAME}'
            response = self._make_get_request(url=api_url)

            if response.status_code == 200:
                data: object = response.json()
                if data.get('coins') != None:
                    self.balance = data['coins']
                else:
                    raise ProfileResponseError('Invalid profile user')
            else:
                raise AuthenticationError('Failed to get user profile data')

        return self.balance

    def send_bet(self, value: int, color: str):
        ''' Make bet '''
        bet_url = 'https://roulette-route.johnpittertv.com/roulette'
        data = {
            'value': value,
            'color': 'verde' if color == '0' else color
        }
        response = self._make_post_request(url=bet_url, body=data)
        
        if response.status_code == 200:
            print(f'-> Bet {value:,.0f} on option {color}')
        else:
            raise AuthenticationError(f'Failed to send bet. (Bet {value:,.0f} on option {color})')

    def im_win(self, aposted_number: str) -> bool:
        response = get(url=f'https://roulette-route.johnpittertv.com/statistics/1')
        
        if response.status_code != 200:
            raise Exception('FATAL: Failed to verify win result')
        
        data = response.json()[0]['number']
        
        print(f'DEBUG: Last one number: {data} Aposted: {aposted_number}')

        if str(aposted_number) == 'verde' and str(data) == '0':
            return True

        return str(data) == str(aposted_number)

    def get_bet_number(self) -> str:
        ''' Return most choiced number in last rounds '''
        response = get(url=f'https://roulette-route.johnpittertv.com/statistics/40')

        if response.status_code != 200:
            raise Exception('FATAL: Failed to get bet number')

        data = response.json()
        compare = {}
        higher_number = None

        for numbers in data:
            number = numbers['number']
            compare[number] = compare[number] + 1 if compare.get(number) != None else 1
        
        for key, value in compare.items():
            if higher_number == None:
                higher_number = {
                    'color': key if key != '0' else 'verde',
                    'bets': value
                }
            else:
                if value >= higher_number['bets']:
                    higher_number = {
                        'color': key if key != '0' else 'verde',
                        'bets': value
                    }

        return higher_number['color']

    def wait_bets_open(self):
        roulette_url = 'https://roulette-route.johnpittertv.com/roulette'
        openned = False

        print('-> Waiting bets open...')

        while not openned:
            response = post(url=roulette_url)
            
            if not 'Aguarde a próxima rodada' in str(response.text):
                openned = True
            
            sleep(3)

        print('-> Bets openned')

    def wait_bets_close(self):
        roulette_url = 'https://roulette-route.johnpittertv.com/roulette'
        closed = False

        print('-> Waiting bets close...')

        while not closed:
            response = post(url=roulette_url)
            
            if 'Aguarde a próxima rodada' in str(response.text):
                closed = True
            
            sleep(3)

        print('-> Bets closed')

    def _make_post_request(self, url: str, body: object) -> Response:
        headers = {
            'Authorization': self.settings.APP_TOKEN,
            'Content-Type': 'application/json'
        }
        response = post(
            url=url, json=body, headers=headers
        )

        return response

    def _make_get_request(self, url: str) -> Response:
        headers = {
            'Authorization': self.settings.APP_TOKEN,
        }
        response = get(url=url, headers=headers)

        return response
