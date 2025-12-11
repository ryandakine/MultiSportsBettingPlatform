import React from 'react';
import { Dialog, DialogActionsBar } from '@progress/kendo-react-dialogs';
import { Form, Field, FormElement } from '@progress/kendo-react-form';
import { Button } from '@progress/kendo-react-buttons';
import { DropDownList } from '@progress/kendo-react-dropdowns';
import { NumericTextBox } from '@progress/kendo-react-inputs';
import StatsCard from './StatsCard';

const BetDialog = ({ game, weatherData, onClose, onSubmit, placingBet }) => {
    if (!game) return null;

    return (
        <Dialog
            title={`Place Bet - ${game.awayTeam} @ ${game.homeTeam}`}
            onClose={onClose}
            width={600}
        >
            <Form
                initialValues={{
                    amount: 100,
                    selection: game.prediction === game.homeTeam ? 'home' : 'away'
                }}
                onSubmit={onSubmit}
                render={(formRenderProps) => (
                    <FormElement style={{ maxWidth: 550 }}>
                        {/* Game Info Card */}
                        <StatsCard game={game} weatherData={weatherData} />

                        {/* Bet Form */}
                        <Field
                            name="selection"
                            component={DropDownList}
                            label="Your Selection"
                            data={[
                                { text: `${game.homeTeam} (${game.odds?.home_ml || game.homeOdds})`, value: 'home' },
                                { text: `${game.awayTeam} (${game.odds?.away_ml || game.awayOdds})`, value: 'away' }
                            ]}
                            textField="text"
                            valueField="value"
                            required={true}
                        />

                        <Field
                            name="amount"
                            component={NumericTextBox}
                            label="Bet Amount ($)"
                            min={10}
                            max={1000}
                            step={10}
                            format="c2"
                            required={true}
                        />

                        <div style={{ marginTop: '16px', padding: '12px', backgroundColor: '#fff3cd', borderRadius: '4px', fontSize: '14px' }}>
                            <p style={{ margin: '0 0 8px 0' }}><strong>⚠️ Betting Responsibly:</strong></p>
                            <ul style={{ margin: 0, paddingLeft: '20px' }}>
                                <li>Only bet what you can afford to lose</li>
                                <li>Set limits and stick to them</li>
                                <li>Never chase losses</li>
                                <li>Consider this entertainment, not investment</li>
                            </ul>
                        </div>

                        <DialogActionsBar>
                            <Button
                                type="submit"
                                themeColor="primary"
                                disabled={placingBet || !formRenderProps.allowSubmit}
                                loading={placingBet}
                            >
                                {placingBet ? 'Placing Bet...' : 'Confirm Bet'}
                            </Button>
                            <Button
                                onClick={onClose}
                                disabled={placingBet}
                            >
                                Cancel
                            </Button>
                        </DialogActionsBar>
                    </FormElement>
                )}
            />
        </Dialog>
    );
};

export default BetDialog;
