package br.com.metaltech.monitoramento.service;

import java.util.List;

import br.com.metaltech.monitoramento.dto.response.ReservatorioResponse;
import br.com.metaltech.monitoramento.entity.Reservatorio;
import br.com.metaltech.monitoramento.repository.ReservatorioRepository;

import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

@Service 
public class ReservatorioService {
    
    private final ReservatorioRepository reservatorioRepository;

    public ReservatorioService(ReservatorioRepository reservatorioRepository) {
        this.reservatorioRepository = reservatorioRepository;
    }

    @Transactional(readOnly = true) 
    public List<ReservatorioResponse> listarTodos() {
        return reservatorioRepository.findAll().stream().map(this::paraResponse).toList();
    }

    private ReservatorioResponse paraResponse(Reservatorio reservatorio) {
        return new ReservatorioResponse(
            reservatorio.getId(),
            reservatorio.getTipoPeca(),
            reservatorio.getCapacidadeMaxima(),
            reservatorio.getQuantidadeAtual(),
            reservatorio.getCiclosCompletos()
        );
    }
}
