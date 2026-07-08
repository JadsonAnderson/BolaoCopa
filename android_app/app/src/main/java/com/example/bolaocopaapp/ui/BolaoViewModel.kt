package com.example.bolaocopaapp.ui

import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.State
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.example.bolaocopaapp.data.model.PalpiteDTO
import com.example.bolaocopaapp.data.model.PartidaDTO
import com.example.bolaocopaapp.data.network.RetrofitClient
import kotlinx.coroutines.launch

class BolaoViewModel : ViewModel() {

    // Estados da Tela (O que o Compose vai observar)
    private val _partidas = mutableStateOf<List<PartidaDTO>>(emptyList())
    val partidas: State<List<PartidaDTO>> = _partidas

    private val _palpites = mutableStateOf<List<PalpiteDTO>>(emptyList())
    val palpites: State<List<PalpiteDTO>> = _palpites

    private val _carregando = mutableStateOf(false)
    val carregando: State<Boolean> = _carregando

    // Bloco que roda assim que o ViewModel é criado
    init {
        carregarDadosIniciais()
    }

    fun carregarDadosIniciais() {
        viewModelScope.launch {
            try {
                _carregando.value = true

                // Busca as partidas e os palpites em paralelo do FastAPI
                val listaPartidas = RetrofitClient.apiService.getPartidas()
                val listaPalpites = RetrofitClient.apiService.getPalpites()

                _partidas.value = listaPartidas
                _palpites.value = listaPalpites
            } catch (e: Exception) {
                // Aqui vocês tratam o erro (ex: backend desligado)
                e.printStackTrace()
            } finally {
                _carregando.value = false
            }
        }
    }

    // Função para Salvar/Atualizar Palpite (POST / PUT)
    fun salvarPalpite(partidaId: Int, golsA: Int, golsB: Int) {
        viewModelScope.launch {
            try {
                val novoPalpite = PalpiteDTO(partidaId, golsA, golsB)

                // Verifica se já existe um palpite para atualizar (PUT) ou criar (POST)
                val jaExiste = _palpites.value.any { it.partidaId == partidaId }

                if (jaExiste) {
                    RetrofitClient.apiService.atualizarPalpite(partidaId, novoPalpite)
                } else {
                    RetrofitClient.apiService.enviarPalpite(novoPalpite)
                }

                // Atualiza a lista local após salvar no banco SQLite
                carregarDadosIniciais()
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }

    // Função para Deletar Palpite (DELETE)
    fun deletarPalpite(partidaId: Int) {
        viewModelScope.launch {
            try {
                RetrofitClient.apiService.deletarPalpite(partidaId)
                carregarDadosIniciais() // Recarrega a lista do banco atualizada
            } catch (e: Exception) {
                e.printStackTrace()
            }
        }
    }
}