package com.example.mgc

import android.os.Bundle
import android.view.LayoutInflater
import android.view.View
import android.view.ViewGroup
import com.example.mgc.databinding.BottomSheetPlantBinding
import com.google.android.material.bottomsheet.BottomSheetDialogFragment

class PlantBottomSheet(
    val isGreenPlacemark: Boolean,
    val plant: Plant
) : BottomSheetDialogFragment() {

    private lateinit var binding: BottomSheetPlantBinding

    override fun onCreateView(
        inflater: LayoutInflater,
        container: ViewGroup?,
        savedInstanceState: Bundle?
    ): View {
        binding = BottomSheetPlantBinding.bind(
            inflater.inflate(
                R.layout.bottom_sheet_plant,
                container
            )
        )

        if (isGreenPlacemark)
            binding.pointsLabel.visibility = View.VISIBLE

        binding.name.text = plant.name
        binding.description.text = plant.description
        binding.age.text = getString(R.string.age, plant.age)
        binding.state.text = getString(R.string.state, plant.state)

        binding.cross.setOnClickListener {
            dismiss()
        }

        binding.confirmBtn.setOnClickListener {
            dismiss()
        }

        binding.problemBtn.setOnClickListener {
            dismiss()
        }

        return binding.root
    }

    override fun getTheme() = R.style.SheetDialog

}