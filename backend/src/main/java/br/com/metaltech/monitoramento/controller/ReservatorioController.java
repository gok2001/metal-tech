package br.com.metaltech.monitoramento.controller;

import br.com.metaltech.monitoramento.dto.response.ReservatorioResponse;
import br.com.metaltech.monitoramento.service.ReservatorioService;

import java.util.List;

import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController 
@RequestMapping("/api/reservatorios") 
public class ReservatorioController {
    
    private final ReservatorioService reservatorioService;

    public ReservatorioController(ReservatorioService reservatorioService) {
        this.reservatorioService = reservatorioService;
    }

    @GetMapping 
    public List<ReservatorioResponse> listarTodos() {
        return reservatorioService.listarTodos();
    }
}
