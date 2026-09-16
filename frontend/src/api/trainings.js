/** API-клиент сессий тренировки. */

import { apiFetch } from './client'

export function startTraining(mode, topic = null) {
  return apiFetch('/trainings/', {
    method: 'POST',
    body: JSON.stringify({ mode, topic }),
  })
}

export function listTrainings() {
  return apiFetch('/trainings/')
}

export function getTraining(trainingId) {
  return apiFetch(`/trainings/${trainingId}`)
}

export function submitAnswer(trainingId, content) {
  return apiFetch(`/trainings/${trainingId}/answers`, {
    method: 'POST',
    body: JSON.stringify({ content }),
  })
}
