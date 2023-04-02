import React, { useEffect, useMemo, useState } from 'react';
import { Card } from 'primereact/card';
import { Button } from 'primereact/button';
import { classNames } from 'primereact/utils';    
import { ProgressBar } from 'primereact/progressbar';
import { ProgressSpinner } from 'primereact/progressspinner'
import { ListBox } from 'primereact/listbox';
import { InputNumber } from 'primereact/inputnumber';
import { InputSwitch } from 'primereact/inputswitch';
import { Dialog } from 'primereact/dialog';

import styles from '../App.module.scss';

export default function MainPage() {
  const [actualState, setActualState] = useState<number>(0);
  const [possibleEnemies, setPossibleEnemies] = useState<{value: number, name: string}[]>();
  const [result, setResult] = useState<{value: number, name: string}[]>();
  const [progress, setProgress] = useState<number>(0);
  const [updateProgressInterval, setUpdateProgressInterval] = useState<number | undefined>(undefined);
  const [submitDisabled, setSubmitDisabled] = useState<boolean>(true);

  const [howItWorksDialogVisible, setHowItWorksDialogVisible] = useState<boolean>(false);
  const [rulesDialogVisible, setRulesDialogVisible] = useState<boolean>(false);

  const [selectedEnemy, setSelectedEnemy] = useState<number>(0);
  const [howManyTurns, setHowManyTurns] = useState<number>();
  const [howManyInGeneration, setHowManyInGeneration] = useState<number>();
  const [howManyGenerations, setHowManyGenerations] = useState<number>();


  const [advancedSettings, setAdvancedSettings] = useState<boolean>(false);
  const [yearsForWinner, setYearsForWinner] = useState<number | undefined>(0);
  const [yearsBothBetray, setYearsBothBetray] = useState<number | undefined>(3);
  const [yearsBothCooperate, setYearsBothCooperate] = useState<number | undefined>(2);
  const [yearsForLoser, setYearsForLoser] = useState<number | undefined>(5);

  useMemo(() => {
    if (progress === 100) {
        clearInterval(updateProgressInterval);
        setUpdateProgressInterval(undefined);
        setActualState(3);
    }
  }, [progress])

  useMemo(async () => {
    if (actualState === 3) {
      await fetch('https://prisoners-dilemma-backend.herokuapp.com/develop-strategy/get-result')
                    .then(res => res.json())
                    .then(json => {
                      let i = 0;
                      setResult(
                        (json as Array<boolean>).map(enemy => {
                          i += 1;
                          return {value: i, name: String(i) + '. ' + (enemy ? 'Cooperate' : 'Betray')};
                        })
                      )
                      setActualState(4);
                    })
                    .catch(e => console.log(e))
    }
  }, [actualState])

  useMemo(() => {
    if (howManyTurns !== undefined && howManyInGeneration !== undefined && howManyGenerations !== undefined 
      && yearsForWinner !== undefined && yearsForLoser !== undefined && yearsBothBetray !== undefined && yearsBothCooperate !== undefined) {
      setSubmitDisabled(false);
    } else {
      setSubmitDisabled(true);
    }
  }, [howManyTurns, howManyInGeneration, howManyGenerations, yearsForWinner, yearsBothBetray, yearsBothCooperate, yearsForLoser])

  useEffect(() => {
    fetch('https://prisoners-dilemma-backend.herokuapp.com/develop-strategy/possible-enemies')
                    .then(res => res.json())
                    .then(json => {
                      setPossibleEnemies(
                        (json as Array<Array<string>>).map(enemy => {
                          return {value: Number(enemy[0]), name: enemy[1]};
                        })
                      )
                    })
                    .catch(e => console.log(e))
  }, [])

  const resetForm = () => {
    setSelectedEnemy(0);
    setHowManyTurns(undefined);
    setHowManyGenerations(undefined);
    setHowManyInGeneration(undefined);
    setAdvancedSettings(false);
    setYearsForWinner(0);
    setYearsBothBetray(5);
    setYearsBothCooperate(3);
    setYearsForLoser(10);
  }

  const resetAdvancedSettings = () => {
    setYearsForWinner(0);
    setYearsBothBetray(5);
    setYearsBothCooperate(3);
    setYearsForLoser(10);
  }

  const findMaxValue = (p1: number, p2: number, p3: number, p4: number) => {
    let maxValue = p1;
    if (p2 > maxValue) {
      maxValue = p2;
    }
    if (p3 > maxValue) {
      maxValue = p3;
    }
    if (p4 > maxValue) {
      maxValue = p4;
    }
    return maxValue;
  }

  return (
    <div
        className={classNames(
          'flex align-items-center justify-content-center',
          styles.pageRoot,
        )}
      >
        <div
          className={classNames(
            'flex align-items-center justify-content-center',
            styles.cardContainer,
          )}
        >
          <Dialog header='How does it work?' className='w-5' visible={howItWorksDialogVisible} onHide={() => setHowItWorksDialogVisible(false)} dismissableMask>
            The tool uses a Non-Dominated Sorting Genetic Algorithm (NSGA-II) to find the best possible tactic for the Prisoner&apos;s Dilemma game. You can choose between seven different enemy strategies.
            <br/><br/>You need to specify, how many turns there are in a game, what the size of a learning population is and how many generations it should take finding the best strategy. 
            Optionally, you can specify, how many years of prison the players get in each possible situation. 
            <br/><br/>After the learning process is done, you are presented with a list of moves you should make for the best strategy found by the algorithm.
          </Dialog>
          <Dialog header='Rules of the game' className='w-7' visible={rulesDialogVisible} onHide={() => setRulesDialogVisible(false)} dismissableMask>
            Two members of a criminal gang, A and B, are arrested and imprisoned. Each prisoner is in solitary confinement with no means of communication with their partner. 
            The principal charge would lead to a sentence of ten years in prison; however, the police do not have the evidence for a conviction. 
            They plan to sentence both to two years in prison on a lesser charge but offer each prisoner a Faustian bargain: 
            If one of them confesses to the crime of the principal charge, betraying the other, they will be pardoned and free to leave while the other must serve the entirety of the sentence instead of just two years for the lesser charge.
            <br/><br/>
            This leads to a possible of four different outcomes:
            <br/>A: If A and B both remain silent, they will each serve the lesser charge of 2 years in prison.
            <br/>B: If A betrays B but B remains silent, A will be set free while B serves 10 years in prison.
            <br/>C: If A remains silent but B betrays A, A will serve 10 years in prison and B will be set free.
            <br/>D: If A and B both betray the other, they share the sentence and serve 5 years.
            <br/><br/>
            The game of Prisoner&apos;s Dilemma consists of multiple turns in which each player knows only what the other player did in the last turn. After all turns are played, the player with the least years of prison wins.
            The rules can be changed by altering the number of years every player gets in each situation.
          </Dialog>
          <Card className='surface-card shadow-2 border-round-2xl w-full lg:w-6 text-center'>
            <div className='grid'>
              <h1 className='col-12 mb-0'>
                Prisoner&apos;s Dilemma
              </h1>
              <h3 className='col-12 mt-0 text-color-secondary mb-2'>
                Best tactic finding tool for the Prisoner&apos;s Dilemma game
              </h3>
              {
                actualState === 0 &&
                <div className='col-12'>
                  <div className='grid'>
                    <div className='col-6'>
                      <Button
                      type='button'
                      label='How does it work?'
                      className='text-2xl w-10 p-2 border-solid border-2 border-round-xl bg-primary-reverse'
                      onClick={() => setHowItWorksDialogVisible(true)}
                      />
                    </div>
                    <div className='col-6'>
                      <Button
                      type='button'
                      label='Rules of the game'
                      className='text-2xl w-10 p-2 border-solid border-2 border-round-xl bg-primary-reverse'
                      onClick={() => setRulesDialogVisible(true)}
                      />
                    </div>
                    <div className='col-12 mt-3'>
                      <Button
                      type='button'
                      label={'Let\'s get started'}
                      className='text-2xl w-8 p-3 border-round-xl'
                      onClick={() => setActualState(1)}
                      />
                    </div>
                  </div>
                </div>
              }
              {
                actualState === 1 &&
                <div className='col-12'>
                  <div className='grid'>
                    <div className='col-12'>
                      <div className='grid'>
                        <div className='col-1'/>
                        <div className='col-5'>
                          <div className='grid'>
                            <span className='col-12 text-left pb-0 text-sm text-color-secondary'>
                              Enemy strategy
                            </span>
                            {
                              !possibleEnemies &&
                              <ProgressSpinner className='mt-8'/>
                            }
                            {
                              possibleEnemies && 
                              <ListBox
                                id='selectedEnemy'
                                value={selectedEnemy}
                                onChange={(e) => setSelectedEnemy(e.value)}
                                options={possibleEnemies}
                                optionLabel='name'
                                className='w-full p-0'
                              /> 
                            }
                          </div>
                        </div>
                        <div className='col-1'/>
                        <div className='col-4 m-auto'>
                          <div className='grid'>
                              <span className='p-float-label col-12 m-auto'>
                                  <InputNumber
                                    id='howMantTurns'
                                    value={howManyTurns}
                                    onChange={(e) => setHowManyTurns(e.value === null ? undefined : e.value)}
                                    className='w-full'
                                    max={1000000}
                                  />
                                  <label htmlFor='howManyTurns'>How many turns</label>
                                </span>
                                <span className='p-float-label col-12 my-5'>
                                  <InputNumber
                                    id='howManyMemebers'
                                    value={howManyInGeneration}
                                    onValueChange={(e) => setHowManyInGeneration(e.value === null ? undefined : e.value)}
                                    className='w-full'
                                    max={1000000}
                                  />
                                  <label htmlFor='howManyMemebers'>How many in population</label>
                                </span>
                                <span className='p-float-label col-12 m-auto'>
                                  <InputNumber
                                    id='howManyGenerations'
                                    value={howManyGenerations}
                                    onChange={(e) => setHowManyGenerations(e.value === null ? undefined : e.value)}
                                    className='w-full'
                                    max={1000000}
                                  />
                                  <label htmlFor='howManyGenerations'>How many generations</label>
                                </span>
                          </div>
                        </div>
                        <div className='col-1'/>
                        <label htmlFor='advancedSettingsSwitch' className='col-12 mt-4 text-color-secondary pb-0'>Advanced settings</label>
                        <div className='col-12 pt-1'>
                          <InputSwitch
                          id='advancedSettingsSwitch'
                          checked={advancedSettings}
                          onChange={(e) => {
                            setAdvancedSettings(e.value);
                            resetAdvancedSettings();
                          }}
                          />
                        </div>
                        {
                          advancedSettings &&
                          <div className='col-12'>
                            <div className='grid'>
                              <div className='col-2'/>
                              <span className='p-float-label col-4 m-auto mt-3'>
                                <InputNumber
                                  id='yearsForWinner'
                                  className='w-full'
                                  value={yearsForWinner}
                                  onValueChange={(e) => setYearsForWinner(e.value === null ? undefined : e.value)}
                                />
                                <label htmlFor='yearsForWinner'>Years for winner</label>
                              </span>
                              <span className='p-float-label col-4 m-auto mt-3'>
                                <InputNumber
                                  id='yearsForLoser'
                                  className='w-full'
                                  value={yearsForLoser}
                                  onValueChange={(e) => setYearsForLoser(e.value === null ? undefined : e.value)}
                                />
                                <label htmlFor='yearsForLoser'>Years for loser</label>
                              </span>
                              <div className='col-2'/>
                              <div className='col-2'/>
                              <span className='p-float-label col-4 m-auto mt-3'>
                                <InputNumber
                                  id='yearsBothCooperate'
                                  className='w-full'
                                  value={yearsBothCooperate}
                                  onValueChange={(e) => setYearsBothCooperate(e.value === null ? undefined : e.value)}
                                />
                                <label htmlFor='yearsBothCooperate'>Years when both cooperate</label>
                              </span>
                              <span className='p-float-label col-4 m-auto mt-3'>
                                <InputNumber
                                  id='yearsBothBetray'
                                  className='w-full'
                                  value={yearsBothBetray}
                                  onValueChange={(e) => setYearsBothBetray(e.value === null ? undefined : e.value)}
                                />
                                <label htmlFor='yearsBothBetray'>Years when both betray</label>
                              </span>
                              <div className='col-2'/>
                            </div>
                          </div>
                        }  
                      </div>
                    </div>
                    <div className='col-12'>
                      <div className='grid'>
                        <div className='col-3'>
                          <Button
                          type='button'
                          label='Go back'
                          className='border-solid border-2 text-xl border-round-xl bg-primary-reverse'
                          onClick={() => {
                            setActualState(0);
                            resetForm();
                          }}
                          />
                        </div>
                        <div className='col-6'>
                        </div>
                        <div className='col-3'>
                          <Button
                          type='button'
                          label='Find strategy'
                          disabled={submitDisabled}
                          className='text-xl border-round-xl'
                          onClick={() => {
                            if(updateProgressInterval === undefined) {
                              const maxYears = findMaxValue(yearsForWinner!, yearsForLoser!, yearsBothBetray!, yearsBothCooperate!)
                              const pointsForWinner = maxYears - yearsForWinner!
                              const pointsForLoser = maxYears - yearsForLoser!
                              const pointsBothBetray = maxYears - yearsBothBetray!
                              const pointsBothCooperate = maxYears - yearsBothCooperate!
                              setActualState(2);
                              setProgress(0);
                              fetch('https://prisoners-dilemma-backend.herokuapp.com/develop-strategy/start/' 
                                  + String(selectedEnemy) + '/' 
                                  + howManyInGeneration + '/'
                                  + howManyTurns + '/'
                                  + howManyGenerations + '/'
                                  + pointsForWinner + '/'
                                  + pointsForLoser + '/'
                                  + pointsBothBetray + '/'
                                  + pointsBothCooperate)
                                  .then(res => res.json())
                                  .then(json => {
                                      if (json === 0) {
                                          setUpdateProgressInterval(setInterval(() => {
                                              fetch('https://prisoners-dilemma-backend.herokuapp.com/develop-strategy/check-progress')
                                                  .then(res => res.json())
                                                  .then(json => {
                                                      setProgress(json)
                                                  })
                                                  .catch(e => console.log(e))
                                          }, 500))
                                      }
                                  })
                                  .catch(e => console.log(e))
                          }
                          }}
                          />
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              }
              {
                actualState === 2 &&
                <div className='col-12'>
                  <ProgressBar value={progress}/>
                </div>
              }
              {
                actualState === 3 &&
                <div className='col-12'>
                  <ProgressSpinner/>
                </div>
              }
              {
                actualState === 4 &&
                <div className='col-12 mt-5'>
                  <div className='grid'>
                    <span className='col-12 font-semibold text-primary text-2xl'>
                      Best strategy found
                    </span>
                    <ListBox
                        options={result}
                        optionLabel='name'
                        className='w-6 m-auto'
                        listStyle={{ height: '300px' }}
                      />
                  </div>
                  <div className='col-12'>
                    <Button
                        type='button'
                        label='Find another strategy'
                        className='text-xl border-round-xl'
                        onClick={() => {
                        setActualState(0);
                        resetForm();
                      }}
                    />
                  </div>
                </div>
              }
            </div>
          </Card>
        </div>
      </div>
  )
}
