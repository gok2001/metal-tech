package br.com.metaltech.monitoramento.controller;

import br.com.metaltech.monitoramento.dto.request.ContagemIntervaloRequest;
import br.com.metaltech.monitoramento.dto.response.ContagemIntervaloHistoricoResponse;
import br.com.metaltech.monitoramento.dto.response.ContagemIntervaloResponse;
import br.com.metaltech.monitoramento.service.ContagemIntervaloService;

import jakarta.validation.Valid;

import java.util.List;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController 
public class ContagemIntervaloController {
    
    private final ContagemIntervaloService contagemService;

    public ContagemIntervaloController(ContagemIntervaloService contagemService) {
        this.contagemService = contagemService;
    }

    @PostMapping("/api/v1/analytics/production") 
    public ResponseEntity<ContagemIntervaloResponse> registrar(
        @Valid @RequestBody ContagemIntervaloRequest request
    ) {
        ContagemIntervaloResponse response = contagemService.registrar(request);

        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }

    @GetMapping("/api/contagens") 
    public List<ContagemIntervaloHistoricoResponse> listarHistorico() {
        return contagemService.listarHistorico();
    }
}
