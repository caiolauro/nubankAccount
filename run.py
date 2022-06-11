from nuService import nuService

if __name__ == '__main__':
    nuService.inititalize()
    nuService.get_credit_card_spend()
    nuService.get_debit_account_spend()
    nuService.merge_credit_and_debit_histories()
    nuService.get_current_savings()
    nuService.update_gsheet()