package com.example.bolaocopaapp

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.viewModels
import androidx.compose.foundation.layout.*
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.*
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.unit.dp
import com.example.bolaocopaapp.ui.BolaoViewModel
import com.example.bolaocopaapp.ui.CardPartida
import com.example.bolaocopaapp.ui.theme.BolaoCopaAppTheme

class MainActivity : ComponentActivity() {

    // Instancia o ViewModel de forma delegada
    private val viewModel: BolaoViewModel by viewModels()

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        setContent {
            BolaoCopaAppTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    BolaoScreen(viewModel)
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BolaoScreen(viewModel: BolaoViewModel) {
    val partidas = viewModel.partidas.value
    val palpites = viewModel.palpites.value
    val carregando = viewModel.carregando.value

    Scaffold(
        topBar = {
            TopAppBar(
                title = { Text("Bolão Copa 2026", color = Color.White) },
                colors = TopAppBarDefaults.topAppBarColors(containerColor = Color(0xFF005088))
            )
        }
    ) { paddingValues ->
        if (carregando) {
            Box(modifier = Modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
                CircularProgressIndicator()
            }
        } else {
            LazyColumn(
                modifier = Modifier
                    .padding(paddingValues)
                    .fillMaxSize()
            ) {
                items(partidas) { partida ->
                    // Procura se já existe um palpite para essa partida no estado do ViewModel
                    val palpiteExistente = palpites.find { it.partidaId == partida.id }

                    CardPartida(
                        partida = partida,
                        palpiteGolsA = palpiteExistente?.golsA?.toString() ?: "",
                        palpiteGolsB = palpiteExistente?.golsB?.toString() ?: "",
                        onSalvar = { gA, gB ->
                            viewModel.salvarPalpite(partida.id, gA, gB)
                        },
                        onDeletar = {
                            viewModel.deletarPalpite(partida.id)
                        }
                    )
                }
            }
        }
    }
}