# Apostador automático baseado nas estatísticas dos últimos
# resultados da roleta.
# www.johnpittertv.com/roleta
from time import sleep, time
from app.settings import BetSettings
from app.core import Core
import logging

class AutoBetting:
    settings: BetSettings = None
    app_core: Core = None
    logger = None

    BET_TOTAL_PROFIT = 0
    BET_TOTAL_LOSS = 0

    TOTAL_ROUNDS = 0

    def __init__(self, settings: BetSettings, logger):
        self.settings = settings
        self.app_core = Core(settings=settings)
        self.logger = logger

        msg = f'''
        --- JohnPitter Auto Betting ---

        Settings:
          Base value: {self.settings.BET_BASE_VALUE}
          Lose multiplier: {self.settings.BET_MULTIPLIER}
          Max rounds to change number: {self.settings.BET_MAX_ROUNDS}
          User balance: {self.app_core.get_user_balance():,.0f}
        '''

        print(msg)
        self.logger.info(msg)

    def show_statistics(self):
        # Calcular e mostrar resultados
        print(f'''\n
        Estatísticas:
          Lucro total: {self.BET_TOTAL_PROFIT:,.0f}
          Perca total: {self.BET_TOTAL_LOSS:,.0f}
          Saldo aproximado: {((self.app_core.balance + self.BET_TOTAL_PROFIT) - (self.BET_TOTAL_LOSS)):,.0f}
        \n''')

        self.logger.info(f'Lucro: {self.BET_TOTAL_PROFIT:,.0f} | Perca: {self.BET_TOTAL_LOSS:,.0f} | Saldo aproximado: {((self.app_core.balance + self.BET_TOTAL_PROFIT) - (self.BET_TOTAL_LOSS)):,.0f}')

    def test(self):
        self.app_core.get_bet_number()

    def start(self, initial_base_number: int = 0):
        # Starts auto betting
        rounds = 0
        bet_number = self.app_core.get_bet_number()
        bet_base_number = initial_base_number if initial_base_number != 0 else self.settings.BET_BASE_VALUE

        print('Bet number choiced:', bet_number)

        if initial_base_number != 0:
            print('Waiting to start new rounds...')
            sleep(10)

        # Wait roulette open
        self.app_core.wait_bets_open()

        while rounds <= self.settings.BET_MAX_ROUNDS:
            if self.TOTAL_ROUNDS >= self.settings.BET_STOP_AFTER_ROUNDS and self.settings.BET_STOP_AFTER_ROUNDS != 0:
                print('-> Total limit reached, stopping bet.')
                exit(0)

            print(f'\n\n{rounds + 1}º round -------------------------------------')

            sleep(0.5)

            try:
                # Send bet
                self.app_core.send_bet(bet_base_number, bet_number)
            except Exception as e:
                print('Failed to make bet', e)

                self.app_core.wait_bets_open()
                continue

            self.logger.info(f'-> Bet send {bet_base_number} in option {bet_number}')

            self.BET_TOTAL_LOSS += bet_base_number

            sleep(2)
            self.app_core.wait_bets_close()

            sleep(16)

            self.app_core.wait_bets_open()

            sleep(1)

            # If i'm win
            if self.app_core.im_win(aposted_number=bet_number):
                profit_value = bet_base_number * 14
                self.BET_TOTAL_PROFIT += profit_value
                
                if self.BET_TOTAL_LOSS > self.BET_TOTAL_PROFIT:
                    self.BET_TOTAL_LOSS -= self.BET_TOTAL_PROFIT
                    self.BET_TOTAL_PROFIT = 0
                else:
                    self.BET_TOTAL_PROFIT = self.BET_TOTAL_PROFIT - self.BET_TOTAL_LOSS
                    self.BET_TOTAL_LOSS = 0

                print(f'''
                ====================
                -> Bet result: WIN ({bet_base_number * 14} coins)
                ====================
                ''')

                self.logger.info(f'-> WIN - {bet_base_number * 14} coins in round {rounds}')

                print('-> Rounds reseted')
                rounds = 0
                self.TOTAL_ROUNDS = 0
                bet_base_number = self.settings.BET_BASE_VALUE
                #exit(0)
            else:
                print('''
                ====================
                -> Bet result: LOSE
                ====================
                ''')

                self.logger.info(f'-> LOSE - {bet_base_number} losed in round {rounds}')
                # Lose, increment bet value
                #if bet_base_number < 1000:
                if bet_base_number < 20:
                    print(f'-> INFO: Valor multiplicado por 1.2')
                    bet_base_number = round(bet_base_number * 1.2) + 1
                elif bet_base_number > 2500:
                    print(f'-> WARN: Valor maior que 2.500 {bet_base_number}')
                    bet_base_number = round(bet_base_number * 1.08) + 1
                else:
                    bet_base_number = round(bet_base_number * self.settings.BET_MULTIPLIER) + 1
                rounds += 1
                self.TOTAL_ROUNDS += 1

            self.show_statistics()

        print('**** Iniciando outro fluxo de rodada ****')
        self.logger.info('**** Iniciando outro fluxo de rodada ****')
        self.start(bet_base_number)

if __name__ == '__main__':
    # Setup logging
    logging.basicConfig(
        filemode='a',
        filename=f'logs/{str(time()).split(".")[0]}.log',
        format='%(asctime)s %(levelname)s %(message)s',
        datefmt='%H:%M:%S',
        level=logging.INFO
    )

    logger = logging.getLogger('AutoBetting')

    settings = BetSettings()

    # Set settings
    settings.BET_BASE_VALUE = 20
    settings.BET_MAX_ROUNDS = 30
    settings.BET_MULTIPLIER = 1.1
    settings.APP_TWITCH_NICKNAME = 'victorh_cepil'
    settings.APP_TOKEN = 'sybdxyfa5fo7ii8b0dq0clkd0v0a6v'
    settings.BET_STOP_AFTER_ROUNDS = 85

    instance = AutoBetting(settings=settings, logger=logger)

    instance.start()
