package com.example.mgc

import android.graphics.Bitmap
import android.graphics.Canvas
import android.os.Bundle
import android.view.View
import android.widget.Toast
import androidx.core.content.ContextCompat
import androidx.fragment.app.Fragment
import com.example.mgc.databinding.FragmentMapBinding
import com.yandex.mapkit.Animation
import com.yandex.mapkit.MapKitFactory
import com.yandex.mapkit.geometry.Point
import com.yandex.mapkit.map.CameraPosition
import com.yandex.mapkit.map.MapObjectTapListener
import com.yandex.runtime.image.ImageProvider

private const val ARG_PARAM1 = "param1"
private const val ARG_PARAM2 = "param2"

class MapFragment : Fragment(R.layout.fragment_map) {
    private lateinit var binding: FragmentMapBinding
    private var latitude: Double = 55.751225
    private var longitude: Double = 37.62954

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        arguments?.let {
            latitude = it.getDouble(ARG_PARAM1)
            longitude = it.getDouble(ARG_PARAM2)
        }
    }

    private val violetPlacemarkTapListener = MapObjectTapListener { obj, point ->
        val dialog = PlantBottomSheet(false, obj.userData as Plant)
        dialog.show((activity as MainActivity).supportFragmentManager, "")
        true
    }

    private val greenPlacemarkTapListener = MapObjectTapListener { obj, point ->
        val dialog = PlantBottomSheet(true, obj.userData as Plant)
        dialog.show((activity as MainActivity).supportFragmentManager, "")
        true
    }

    override fun onViewCreated(view: View, savedInstanceState: Bundle?) {
        super.onViewCreated(view, savedInstanceState)
        binding = FragmentMapBinding.bind(view)

        binding.mapView.mapWindow.map.move(
            CameraPosition(
                Point(latitude, longitude),
                /* zoom = */ 17.0f,
                /* azimuth = */ 0.0f,
                /* tilt = */ 30.0f
            )
        )

        val violetPlants = listOf(
            Plant(point = Point(56.323857, 44.041995)),
            Plant(point = Point(56.329663, 44.019101)),
            Plant(point = Point(56.320668, 44.042089)),
            Plant(point = Point(56.322048, 44.017381)),
            Plant(point = Point(56.326535, 43.985727))
        )
        val greenPlants = listOf(
            Plant(
                name = getString(R.string.birch),
                description = getString(R.string.birch_description),
                state = "удовлетворительное",
                point = Point(56.324221, 44.037923)
            ),
            Plant(
                name = getString(R.string.birch),
                description = getString(R.string.birch_description),
                state = "удовлетворительное",
                point = Point(56.315718, 44.007497)
            ),
            Plant(
                name = getString(R.string.birch),
                description = getString(R.string.birch_description),
                state = "удовлетворительное",
                point = Point(56.327612, 44.035169)
            )
        )
        val violetImageProvider =
            ImageProvider.fromBitmap(createBitmapFromVector(R.drawable.location_violet))
        val greenImageProvider =
            ImageProvider.fromBitmap(createBitmapFromVector(R.drawable.location_green))
        for (plant in violetPlants) {
            val placemark = binding.mapView.map.mapObjects.addPlacemark().apply {
                geometry = Point(plant.point.latitude, plant.point.longitude)
                setIcon(violetImageProvider)
                userData = plant
            }
            placemark.addTapListener(violetPlacemarkTapListener)
        }
        for (plant in greenPlants) {
            val placemark = binding.mapView.map.mapObjects.addPlacemark().apply {
                geometry = Point(plant.point.latitude, plant.point.longitude)
                setIcon(greenImageProvider)
                userData = plant
            }
            placemark.addTapListener(greenPlacemarkTapListener)
        }
    }

    private fun createBitmapFromVector(art: Int): Bitmap? {
        val drawable = ContextCompat.getDrawable(requireContext(), art) ?: return null
        val bitmap = Bitmap.createBitmap(
            drawable.intrinsicWidth,
            drawable.intrinsicHeight,
            Bitmap.Config.ARGB_8888
        ) ?: return null
        val canvas = Canvas(bitmap)
        drawable.setBounds(0, 0, canvas.width, canvas.height)
        drawable.draw(canvas)
        return bitmap
    }

    override fun onStart() {
        super.onStart()
        MapKitFactory.getInstance().onStart()
        binding.mapView.onStart()
    }

    override fun onStop() {
        binding.mapView.onStop()
        MapKitFactory.getInstance().onStop()
        super.onStop()
    }

    companion object {
        @JvmStatic
        fun newInstance(param1: Double, param2: Double) =
            MapFragment().apply {
                arguments = Bundle().apply {
                    putDouble(ARG_PARAM1, param1)
                    putDouble(ARG_PARAM2, param2)
                }
            }
    }
}