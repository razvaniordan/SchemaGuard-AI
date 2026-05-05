package com.example.api.service;

import com.example.api.dto.request.MccCodeRequest;
import com.example.api.dto.response.MccCodeResponse;
import com.example.api.entity.MccCode;
import com.example.api.repository.MccCodeRepository;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.List;

@Service
public class MccCodeService {
    private final MccCodeRepository mccCodeRepository;

    public MccCodeService(MccCodeRepository mccCodeRepository) {
        this.mccCodeRepository = mccCodeRepository;
    }

    @Transactional(readOnly = true)
    public List<MccCodeResponse> findAll() {
        return mccCodeRepository.findAll().stream().map(this::toResponse).toList();
    }

    @Transactional
    public MccCodeResponse create(MccCodeRequest request) {
        MccCode mccCode = MccCode.builder()
                .mccCode(request.mccCode())
                .mccDescription(request.mccDescription())
                .build();
        return toResponse(mccCodeRepository.save(mccCode));
    }

    private MccCodeResponse toResponse(MccCode mccCode) {
        return new MccCodeResponse(mccCode.getMccCode(), mccCode.getMccDescription());
    }
}
