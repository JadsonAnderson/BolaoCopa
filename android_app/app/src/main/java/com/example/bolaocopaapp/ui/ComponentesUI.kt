package com.example.bolaocopaapp.ui

import androidx.compose.foundation.layout.*
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.filled.Delete
import androidx.compose.material.icons.filled.Check
import androidx.compose.material3.*
import androidx.compose.runtime.*
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.text.input.KeyboardType
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import coil.compose.AsyncImage
import com.example.bolaocopaapp.data.model.PartidaDTO

@Composable
fun CardPartida(
    partida: PartidaDTO,
    palpiteGolsA: String,
    palpiteGolsB: String,
    onSalvar: (Int, Int) -> Unit,
    onDeletar: () -> Unit
) {
    // Estados locais para os campos de texto do card
    var golsA by remember { mutableStateOf(palpiteGolsA) }
    var golsB by remember { mutableStateOf(palpiteGolsB) }

    Card(
        modifier = Modifier
            .fillMaxWidth()
            .padding(8.dp),
        elevation = CardDefaults.cardElevation(4.dp),
        colors = CardDefaults.cardColors(containerColor = Color(0xFFF1F5F9))
    ) {
        Column(
            modifier = Modifier.padding(16.dp),
            horizontalAlignment = Alignment.CenterHorizontally
        ) {
            Text(
                text = "Copa do Mundo 2026 - ${partida.dataJogo}",
                style = MaterialTheme.typography.labelMedium,
                color = Color.Gray
            )

            Row(
                modifier = Modifier
                    .fillMaxWidth()
                    .padding(vertical = 12.dp),
                horizontalArrangement = Arrangement.SpaceBetween,
                verticalAlignment = Alignment.CenterVertically
            ) {
                // Time A
                Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.weight(1f)) {
                    AsyncImage(
                        model = partida.bandeiraA,
                        contentDescription = null,
                        modifier = Modifier.size(50.dp)
                    )
                    Text(partida.timeA, fontWeight = FontWeight.Bold)
                }

                // Inputs de Placar
                Row(verticalAlignment = Alignment.CenterVertically) {
                    OutlinedTextField(
                        value = golsA,
                        onValueChange = { golsA = it },
                        modifier = Modifier.width(50.dp),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        singleLine = true
                    )
                    Text(" X ", fontSize = 20.sp, fontWeight = FontWeight.Bold)
                    OutlinedTextField(
                        value = golsB,
                        onValueChange = { golsB = it },
                        modifier = Modifier.width(50.dp),
                        keyboardOptions = KeyboardOptions(keyboardType = KeyboardType.Number),
                        singleLine = true
                    )
                }

                // Time B
                Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.weight(1f)) {
                    AsyncImage(
                        model = partida.bandeiraB,
                        contentDescription = null,
                        modifier = Modifier.size(50.dp)
                    )
                    Text(partida.timeB, fontWeight = FontWeight.Bold)
                }
            }

            // Botões de Ação
            Row(modifier = Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.End) {
                IconButton(onClick = onDeletar) {
                    Icon(Icons.Default.Delete, contentDescription = "Deletar", tint = Color.Red)
                }
                Button(
                    onClick = {
                        val gA = golsA.toIntOrNull() ?: 0
                        val gB = golsB.toIntOrNull() ?: 0
                        onSalvar(gA, gB)
                    },
                    colors = ButtonDefaults.buttonColors(containerColor = Color(0xFF005088))
                ) {
                    Icon(Icons.Default.Check, contentDescription = null)
                    Spacer(Modifier.width(4.dp))
                    Text("Salvar")
                }
            }
        }
    }
}