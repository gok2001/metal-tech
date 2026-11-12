package br.com.metaltech.monitoramento.controller;

import br.com.metaltech.monitoramento.dto.request.ContagemIntervaloRequest;
import br.com.metaltech.monitoramento.dto.response.ContagemIntervaloResponse;
import br.com.metaltech.monitoramento.service.ContagemIntervaloService;

import jakarta.validation.Valid;

import org.springframework.http.HttpStatus;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

@RestController 
@RequestMapping("/api/contagens") 
public class ContagemIntervaloController {
    
    private final ContagemIntervaloService contagemService;

    public ContagemIntervaloController(ContagemIntervaloService contagemService) {
        this.contagemService = contagemService;
    }

    @PostMapping 
    public ResponseEntity<ContagemIntervaloResponse> registrar(
        @Valid @RequestBody ContagemIntervaloRequest request
    ) {
        ContagemIntervaloResponse response = contagemService.registrar(request);

        return ResponseEntity.status(HttpStatus.CREATED).body(response);
    }
}
